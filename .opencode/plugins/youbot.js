// you.bot provider for opencode.
//
// you.bot (https://you.bot) is not OpenAI-compatible: it exposes one endpoint,
// POST https://you.bot/api/v1/generate with { modelId, input }. This plugin
// starts a tiny local OpenAI-compatible shim and registers a "youbot" provider
// pointing at it, so opencode can use you.bot models.
//
// Setup: set YOUBOT_API_KEY before starting opencode, then restart opencode
// and pick the model with /models.
//
// Caveat: you.bot's API has no tool/function calling, so this model is
// chat-only in opencode (it can answer, but cannot edit files or run tools).

const YOUBOT_URL = "https://you.bot/api/v1/generate"

// Add more you.bot model ids here as needed.
const MODELS = {
  "gpt-6-luna": {
    name: "GPT-6 Luna (you.bot)",
    tool_call: false,
    // ponytail: you.bot does not document context/output limits; tune if needed.
    limit: { context: 128000, output: 32768 },
  },
}

function textOf(content) {
  if (typeof content === "string") return content
  if (Array.isArray(content)) {
    return content
      .filter((part) => part && (part.type === "text" || part.type === "input_text"))
      .map((part) => part.text ?? "")
      .join("\n")
  }
  return ""
}

function toYoubotRequest(body) {
  const messages = []
  const system = []
  for (const message of body.messages ?? []) {
    const content = textOf(message.content).trim()
    if (!content) continue
    if (message.role === "system") system.push(content)
    else if (message.role === "user" || message.role === "assistant") messages.push({ role: message.role, content })
  }
  // ponytail: you.bot caps conversations at 20 messages; older turns are dropped.
  // max_tokens is deliberately not forwarded: gpt-6-luna does not accept it.
  const input = {}
  if (messages.length) input.messages = messages.slice(-20)
  else if (system.length) input.prompt = system.join("\n\n")
  if (system.length && messages.length) input.system = system.join("\n\n")
  if (body.stream) input.stream = true
  return { modelId: body.model, input }
}

function completion(model, text, usage) {
  const prompt = usage?.inputTokens ?? 0
  const output = usage?.outputTokens ?? 0
  return {
    id: "chatcmpl-youbot",
    object: "chat.completion",
    created: Math.floor(Date.now() / 1000),
    model,
    choices: [{ index: 0, message: { role: "assistant", content: text ?? "" }, finish_reason: "stop" }],
    usage: { prompt_tokens: prompt, completion_tokens: output, total_tokens: prompt + output },
  }
}

function sseStream(upstream, model) {
  const encoder = new TextEncoder()
  const decoder = new TextDecoder()
  const id = "chatcmpl-youbot"
  const created = Math.floor(Date.now() / 1000)
  const stream = new ReadableStream({
    async start(controller) {
      const send = (obj) => controller.enqueue(encoder.encode(`data: ${JSON.stringify(obj)}\n\n`))
      const chunk = (delta, finish_reason = null) =>
        send({ id, object: "chat.completion.chunk", created, model, choices: [{ index: 0, delta, finish_reason }] })
      chunk({ role: "assistant", content: "" })
      const reader = upstream.body.getReader()
      let buffer = ""
      try {
        for (;;) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split("\n")
          buffer = lines.pop() ?? ""
          for (const line of lines) {
            if (!line.startsWith("data:")) continue
            const payload = line.slice(5).trim()
            if (!payload) continue
            let event
            try {
              event = JSON.parse(payload)
            } catch {
              continue
            }
            if (typeof event.text === "string" && event.text) chunk({ content: event.text })
          }
        }
        chunk({}, "stop")
        controller.enqueue(encoder.encode("data: [DONE]\n\n"))
      } finally {
        controller.close()
      }
    },
  })
  return new Response(stream, { headers: { "content-type": "text/event-stream", "cache-control": "no-cache" } })
}

function makeHandler() {
  return async (request) => {
    const url = new URL(request.url)
    if (request.method !== "POST" || !url.pathname.endsWith("/chat/completions")) {
      return Response.json({ error: { message: "not found" } }, { status: 404 })
    }
    let body
    try {
      body = await request.json()
    } catch {
      return Response.json({ error: { message: "invalid JSON" } }, { status: 400 })
    }
    const header = request.headers.get("authorization") ?? ""
    const key = process.env.YOUBOT_API_KEY || header.replace(/^Bearer\s+/i, "")
    if (!key) {
      return Response.json(
        { error: { message: "Set YOUBOT_API_KEY before starting opencode to use you.bot." } },
        { status: 401 },
      )
    }
    let upstream
    try {
      upstream = await fetch(YOUBOT_URL, {
        method: "POST",
        headers: { authorization: `Bearer ${key}`, "content-type": "application/json" },
        body: JSON.stringify(toYoubotRequest(body)),
      })
    } catch (error) {
      return Response.json({ error: { message: `you.bot request failed: ${error}` } }, { status: 502 })
    }
    if (!upstream.ok) {
      const detail = (await upstream.text()).slice(0, 500)
      return Response.json({ error: { message: `you.bot ${upstream.status}: ${detail}` } }, { status: upstream.status })
    }
    if (body.stream) return sseStream(upstream, body.model)
    const data = await upstream.json()
    return Response.json(completion(body.model, data.text, data.usage))
  }
}

export const YoubotPlugin = async () => {
  if (typeof Bun === "undefined") return {}
  const server = Bun.serve({ hostname: "127.0.0.1", port: 0, fetch: makeHandler() })
  return {
    config: (cfg) => {
      cfg.provider ??= {}
      cfg.provider.youbot = {
        name: "you.bot",
        npm: "@ai-sdk/openai-compatible",
        options: { baseURL: `http://127.0.0.1:${server.port}/v1` },
        models: MODELS,
      }
    },
    dispose: async () => {
      server.stop(true)
    },
  }
}

if (import.meta.main) {
  const assert = (await import("node:assert/strict")).default
  const request = toYoubotRequest({
    model: "gpt-6-luna",
    stream: true,
    messages: [
      { role: "system", content: "sys" },
      { role: "user", content: [{ type: "text", text: "hi" }] },
      { role: "assistant", content: [] },
    ],
  })
  assert.equal(request.modelId, "gpt-6-luna")
  assert.equal(request.input.system, "sys")
  assert.deepEqual(request.input.messages, [{ role: "user", content: "hi" }])
  assert.equal(request.input.stream, true)
  const response = completion("gpt-6-luna", "hello", { inputTokens: 5, outputTokens: 2 })
  assert.equal(response.choices[0].message.content, "hello")
  assert.equal(response.usage.total_tokens, 7)
  console.log("youbot plugin self-check ok")
}
