{
  "product": {
    "name": "Smart Decision AI",
    "design_personality": [
      "premium",
      "minimal",
      "calmly intelligent",
      "high-clarity",
      "Linear/Vercel-like density",
      "Notion-like readability"
    ],
    "north_star": "Make complex decisions feel simple: one question at a time, instant feedback, and a results dashboard that feels authoritative and celebratory.",
    "mobile_first": true,
    "dark_first": true
  },
  "design_tokens": {
    "notes": [
      "Use semantic tokens (background/surface/text/border) rather than hard-coded colors.",
      "Avoid purple. Accent should be ocean/teal + a warm peach for highlights.",
      "Gradients are decorative only and must stay under 20% viewport area."
    ],
    "css_custom_properties": {
      "file": "/app/frontend/src/index.css",
      "instructions": [
        "Replace the default shadcn :root and .dark HSL values with the palette below.",
        "Keep token names the same to preserve shadcn compatibility.",
        "Add extra custom tokens under :root for shadows, blur, and spacing." 
      ],
      "palette_light_hsl": {
        "--background": "210 33% 99%",
        "--foreground": "222 47% 11%",
        "--card": "0 0% 100%",
        "--card-foreground": "222 47% 11%",
        "--popover": "0 0% 100%",
        "--popover-foreground": "222 47% 11%",
        "--primary": "196 84% 38%",
        "--primary-foreground": "210 40% 98%",
        "--secondary": "210 24% 96%",
        "--secondary-foreground": "222 47% 11%",
        "--muted": "210 24% 96%",
        "--muted-foreground": "215 16% 40%",
        "--accent": "24 92% 92%",
        "--accent-foreground": "222 47% 11%",
        "--destructive": "0 84% 56%",
        "--destructive-foreground": "210 40% 98%",
        "--border": "214 20% 90%",
        "--input": "214 20% 90%",
        "--ring": "196 84% 38%",
        "--chart-1": "196 84% 38%",
        "--chart-2": "173 58% 39%",
        "--chart-3": "24 92% 60%",
        "--chart-4": "210 10% 55%",
        "--chart-5": "222 47% 35%",
        "--radius": "0.75rem",
        "--shadow-1": "0 1px 2px hsl(222 47% 11% / 0.06)",
        "--shadow-2": "0 10px 30px hsl(222 47% 11% / 0.10)",
        "--shadow-3": "0 18px 60px hsl(222 47% 11% / 0.14)",
        "--glass-bg": "hsl(0 0% 100% / 0.65)",
        "--glass-border": "hsl(214 20% 90% / 0.7)",
        "--noise-opacity": "0.06"
      },
      "palette_dark_hsl": {
        "--background": "222 47% 6%",
        "--foreground": "210 40% 98%",
        "--card": "222 47% 8%",
        "--card-foreground": "210 40% 98%",
        "--popover": "222 47% 8%",
        "--popover-foreground": "210 40% 98%",
        "--primary": "196 84% 52%",
        "--primary-foreground": "222 47% 8%",
        "--secondary": "222 28% 14%",
        "--secondary-foreground": "210 40% 98%",
        "--muted": "222 28% 14%",
        "--muted-foreground": "215 20% 70%",
        "--accent": "24 70% 22%",
        "--accent-foreground": "24 92% 92%",
        "--destructive": "0 62% 38%",
        "--destructive-foreground": "210 40% 98%",
        "--border": "222 22% 18%",
        "--input": "222 22% 18%",
        "--ring": "196 84% 52%",
        "--chart-1": "196 84% 52%",
        "--chart-2": "173 58% 45%",
        "--chart-3": "24 92% 60%",
        "--chart-4": "210 10% 65%",
        "--chart-5": "210 40% 98%",
        "--radius": "0.85rem",
        "--shadow-1": "0 1px 2px hsl(0 0% 0% / 0.35)",
        "--shadow-2": "0 14px 40px hsl(0 0% 0% / 0.45)",
        "--shadow-3": "0 24px 80px hsl(0 0% 0% / 0.55)",
        "--glass-bg": "hsl(222 47% 10% / 0.55)",
        "--glass-border": "hsl(222 22% 22% / 0.7)",
        "--noise-opacity": "0.08"
      }
    },
    "spacing_system": {
      "base": "4px",
      "scale_px": [
        4,
        8,
        12,
        16,
        20,
        24,
        32,
        40,
        48,
        64,
        80
      ],
      "layout_rules": [
        "Use 24–32px vertical padding for sections on mobile; 48–80px on desktop.",
        "Cards: 16px padding mobile, 20–24px desktop.",
        "Wizard: keep one primary action per screen; secondary actions as ghost buttons."
      ]
    },
    "radius": {
      "card": "rounded-xl",
      "button": "rounded-lg",
      "input": "rounded-lg",
      "pill": "rounded-full (only for small badges/chips)"
    },
    "shadows": {
      "light": {
        "card": "shadow-[var(--shadow-1)] hover:shadow-[var(--shadow-2)]",
        "floating": "shadow-[var(--shadow-2)]"
      },
      "dark": {
        "card": "shadow-[var(--shadow-1)] hover:shadow-[var(--shadow-2)]",
        "floating": "shadow-[var(--shadow-2)]"
      }
    }
  },
  "typography": {
    "font_pairing": {
      "primary": {
        "name": "Inter",
        "usage": "UI + body + forms",
        "weights": [
          400,
          500,
          600,
          700
        ]
      },
      "display_optional": {
        "name": "Space Grotesk",
        "usage": "Hero headline only (landing + results hero). Keep subtle; do not use everywhere.",
        "weights": [
          500,
          600,
          700
        ]
      }
    },
    "type_scale_tailwind": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl tracking-tight",
      "h2": "text-base md:text-lg text-muted-foreground",
      "section_title": "text-xl sm:text-2xl font-semibold tracking-tight",
      "card_title": "text-base font-semibold",
      "body": "text-sm sm:text-base leading-relaxed",
      "caption": "text-xs text-muted-foreground"
    },
    "copy_rules": [
      "Prefer short sentences. Use bullets for pros/cons.",
      "Use numbers and labels consistently: Score 0–100, Confidence %, Risk: Low/Med/High.",
      "Avoid hype words; sound calm and trustworthy."
    ]
  },
  "layout": {
    "grid": {
      "container": "mx-auto w-full max-w-6xl px-4 sm:px-6 lg:px-8",
      "dashboard": "grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-6",
      "dashboard_left": "lg:col-span-8",
      "dashboard_right": "lg:col-span-4",
      "cards": "grid grid-cols-1 md:grid-cols-2 gap-4"
    },
    "navigation": {
      "top_nav": {
        "style": "sticky top-0 z-50 backdrop-blur supports-[backdrop-filter]:bg-background/70 border-b",
        "height": "h-14",
        "content": "Left: logo + product name; Center (desktop): nav links; Right: theme toggle + Saved Decisions + primary CTA",
        "data_testids": {
          "theme_toggle": "theme-toggle",
          "nav_saved": "nav-saved-decisions-link",
          "nav_new": "nav-new-decision-link"
        }
      }
    }
  },
  "components": {
    "component_path": {
      "shadcn_primary": "/app/frontend/src/components/ui/",
      "use_components": [
        "button.jsx",
        "card.jsx",
        "progress.jsx",
        "tabs.jsx",
        "table.jsx",
        "badge.jsx",
        "separator.jsx",
        "skeleton.jsx",
        "dialog.jsx",
        "drawer.jsx",
        "tooltip.jsx",
        "switch.jsx",
        "slider.jsx",
        "radio-group.jsx",
        "checkbox.jsx",
        "select.jsx",
        "textarea.jsx",
        "input.jsx",
        "sonner.jsx"
      ]
    },
    "buttons": {
      "variants": {
        "primary": {
          "use": "<Button> default variant",
          "tailwind_overrides": "bg-primary text-primary-foreground hover:bg-primary/90",
          "motion": "hover: translateY(-1px) + shadow increase; active: scale(0.98)",
          "data_testid_examples": [
            "landing-hero-cta-button",
            "wizard-next-button",
            "results-save-decision-button",
            "results-export-pdf-button"
          ]
        },
        "secondary": {
          "use": "variant=secondary",
          "tailwind_overrides": "bg-secondary text-secondary-foreground hover:bg-secondary/80"
        },
        "ghost": {
          "use": "variant=ghost",
          "tailwind_overrides": "hover:bg-accent/40"
        },
        "destructive": {
          "use": "variant=destructive",
          "tailwind_overrides": "bg-destructive text-destructive-foreground hover:bg-destructive/90",
          "data_testid_examples": [
            "saved-decision-delete-button"
          ]
        }
      },
      "sizes": {
        "sm": "h-9 px-3",
        "md": "h-10 px-4",
        "lg": "h-11 px-5"
      }
    },
    "inputs": {
      "text": {
        "component": "input.jsx",
        "classes": "bg-background/60 dark:bg-background/30 backdrop-blur border-border focus-visible:ring-2 focus-visible:ring-ring",
        "data_testid_examples": [
          "wizard-decision-title-input",
          "wizard-followup-text-input"
        ]
      },
      "textarea": {
        "component": "textarea.jsx",
        "classes": "min-h-[120px] resize-none",
        "data_testid_examples": [
          "wizard-decision-statement-textarea"
        ]
      },
      "slider": {
        "component": "slider.jsx",
        "usage": "What-if simulation + numeric preference questions",
        "data_testid_examples": [
          "wizard-preference-slider",
          "whatif-salary-slider"
        ]
      },
      "single_choice": {
        "component": "radio-group.jsx",
        "pattern": "Use card-like radio items (Card + RadioGroupItem) for premium feel.",
        "data_testid_examples": [
          "wizard-single-choice"
        ]
      },
      "multi_choice": {
        "component": "checkbox.jsx",
        "pattern": "Use checkbox chips inside a flex-wrap container; show selected count.",
        "data_testid_examples": [
          "wizard-multi-choice"
        ]
      },
      "select": {
        "component": "select.jsx",
        "usage": "Only when options > 6; otherwise use radio cards.",
        "data_testid_examples": [
          "wizard-select"
        ]
      }
    },
    "wizard": {
      "layout": {
        "shell": "min-h-[calc(100vh-56px)]",
        "center_column": "mx-auto w-full max-w-2xl px-4 sm:px-6",
        "question_card": "rounded-2xl border bg-card/70 dark:bg-card/50 backdrop-blur shadow-[var(--shadow-1)]",
        "footer_actions": "flex items-center justify-between gap-3 pt-4"
      },
      "progress_indicator": {
        "component": "progress.jsx",
        "pattern": "Top sticky mini-header inside wizard: step label + Progress bar + step dots.",
        "dots": "Use 6–10px dots with completed check icon (lucide Check) and subtle scale-in animation.",
        "data_testid": "wizard-progress"
      },
      "micro_interactions": [
        "Animate step transitions with Framer Motion: slide 12px + fade; keep duration 0.22–0.28s.",
        "On answer selection: immediate highlight + subtle haptic-like scale (scale 1.01 then settle).",
        "Disable Next until valid; show inline helper text rather than toast for validation."
      ],
      "review_step": {
        "pattern": "Before analysis, show a compact summary (Accordion) of answers with Edit links.",
        "components": [
          "accordion.jsx",
          "button.jsx",
          "separator.jsx"
        ],
        "data_testids": {
          "review_edit": "wizard-review-edit-link",
          "review_submit": "wizard-review-submit-button"
        }
      }
    },
    "loading_analysis": {
      "components": [
        "skeleton.jsx",
        "card.jsx"
      ],
      "pattern": "Use a 'thinking' panel: animated shimmer skeleton + rotating insight phrases (every 1.2s). Keep it calm, not playful.",
      "motion": {
        "framer": {
          "stagger": 0.06,
          "duration": 0.28,
          "ease": "[0.22, 1, 0.36, 1]"
        }
      },
      "data_testid": "analysis-loading-state"
    },
    "results_dashboard": {
      "best_option_hero": {
        "pattern": "Large hero card with score (0–100), confidence meter, and a single-sentence rationale.",
        "classes": "rounded-2xl border bg-card/70 dark:bg-card/50 backdrop-blur shadow-[var(--shadow-2)]",
        "accent": "Use a thin top border highlight: border-t-2 border-t-primary/60 (no gradients).",
        "data_testid": "results-best-option-card"
      },
      "ranked_options": {
        "pattern": "Stacked cards with animated score bars (Progress) and quick pros/cons preview.",
        "components": [
          "card.jsx",
          "progress.jsx",
          "badge.jsx"
        ],
        "data_testid": "results-ranked-options"
      },
      "score_visualization": {
        "library": "recharts",
        "charts": [
          "Horizontal bar chart for option scores",
          "Small sparkline for sensitivity (what-if)"
        ],
        "style": "Minimal axes, muted gridlines, tooltip with Card-like surface.",
        "data_testid": "results-score-chart"
      },
      "pros_cons_table": {
        "component": "table.jsx",
        "pattern": "Comparison table with sticky first column on desktop; on mobile collapse into Tabs per option.",
        "data_testid": "results-pros-cons-table"
      },
      "confidence_meter": {
        "component": "progress.jsx",
        "pattern": "Confidence as a meter with label + numeric percent; color shifts: <40 muted, 40–70 primary, >70 primary + subtle glow shadow.",
        "data_testid": "results-confidence-meter"
      },
      "what_if": {
        "pattern": "Right rail panel with sliders/selects; updates chart + scores with 200ms debounce.",
        "components": [
          "slider.jsx",
          "select.jsx",
          "card.jsx"
        ],
        "data_testid": "results-whatif-panel"
      },
      "side_by_side": {
        "pattern": "Use Tabs: 'Overview' | 'Compare'. Compare view uses 2–3 columns on desktop, carousel on mobile.",
        "components": [
          "tabs.jsx",
          "carousel.jsx",
          "card.jsx"
        ],
        "data_testid": "results-compare-mode"
      }
    },
    "saved_decisions": {
      "list": {
        "pattern": "Card list with decision title, date, top option, and score. Hover reveals actions.",
        "components": [
          "card.jsx",
          "dropdown-menu.jsx",
          "dialog.jsx",
          "badge.jsx"
        ],
        "data_testids": {
          "list": "saved-decisions-list",
          "open": "saved-decision-open-button",
          "delete": "saved-decision-delete-button"
        }
      },
      "empty_state": {
        "pattern": "Centered within content column (not whole page). Use a subtle illustration block + CTA.",
        "components": [
          "card.jsx",
          "button.jsx"
        ],
        "data_testid": "saved-decisions-empty-state"
      }
    },
    "pdf_export": {
      "library": "jspdf",
      "pattern": "Export button opens Dialog with export options (include what-if settings, include comparison table).",
      "components": [
        "dialog.jsx",
        "checkbox.jsx",
        "button.jsx"
      ],
      "data_testid": "results-export-dialog"
    },
    "toasts": {
      "library": "sonner",
      "component": "/app/frontend/src/components/ui/sonner.jsx",
      "usage": "Only for global events: saved, deleted, export started/finished, network errors.",
      "data_testid": "global-toast"
    }
  },
  "motion": {
    "principles": [
      "Motion communicates state change (step transitions, score updates), not decoration.",
      "Keep durations short; prefer easing that feels 'snappy but soft'.",
      "Respect prefers-reduced-motion: disable parallax and reduce entrance animations."
    ],
    "framer_motion": {
      "easing": "[0.22, 1, 0.36, 1]",
      "durations_s": {
        "micro": 0.12,
        "ui": 0.22,
        "panel": 0.28,
        "celebrate": 0.36
      },
      "patterns": {
        "step_transition": {
          "initial": "{ opacity: 0, y: 12 }",
          "animate": "{ opacity: 1, y: 0 }",
          "exit": "{ opacity: 0, y: -8 }"
        },
        "score_countup": "Animate number from previous score to new score over 280ms; bar fills slightly delayed (60ms).",
        "hover_lift": "On cards: translateY(-2px) + shadow increase; do not animate transform via transition: all."
      }
    }
  },
  "visual_effects": {
    "glassmorphism": {
      "rules": [
        "Use glass only on nav and hero cards; keep readability high.",
        "Use backdrop-blur-md and bg-[var(--glass-bg)] with border-[var(--glass-border)]."
      ],
      "tailwind_snippet": "backdrop-blur-md bg-[var(--glass-bg)] border border-[var(--glass-border)]"
    },
    "noise_overlay": {
      "pattern": "Add a subtle CSS noise overlay on the app background (pseudo-element) with opacity var(--noise-opacity).",
      "css_snippet": ".app-noise::before{content:'';position:fixed;inset:0;pointer-events:none;background-image:url('data:image/svg+xml;utf8,<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"160\" height=\"160\"><filter id=\"n\"><feTurbulence type=\"fractalNoise\" baseFrequency=\"0.9\" numOctaves=\"3\" stitchTiles=\"stitch\"/></filter><rect width=\"160\" height=\"160\" filter=\"url(%23n)\" opacity=\"0.35\"/></svg>');opacity:var(--noise-opacity);mix-blend-mode:overlay;z-index:0;}"
    },
    "gradients": {
      "allowed_usage": [
        "Landing hero background only (max 20% viewport)",
        "Decorative corner glow behind hero card"
      ],
      "safe_gradient_examples": [
        "from-slate-950 via-slate-950 to-slate-900 (dark subtle)",
        "from-teal-500/10 via-cyan-500/5 to-transparent (accent glow)"
      ]
    }
  },
  "pages": {
    "landing": {
      "sections": [
        "Hero (headline + CTA + mini demo card)",
        "Value props (3 cards)",
        "How it works (wizard preview)",
        "Social proof (logos + 2 testimonials)",
        "CTA band (solid, no gradient)",
        "Footer"
      ],
      "hero_layout": "Two-column on desktop: left copy, right interactive demo card (fake wizard step). Single column on mobile.",
      "data_testids": {
        "cta_primary": "landing-hero-cta-button",
        "cta_secondary": "landing-secondary-cta-button"
      }
    },
    "wizard": {
      "steps": [
        "Decision statement",
        "Constraints",
        "Preferences",
        "Risk tolerance",
        "Review",
        "Analyze"
      ]
    },
    "results": {
      "sections": [
        "Best option hero",
        "Ranked options",
        "Charts",
        "Pros/cons comparison",
        "What-if panel",
        "Save + Export"
      ]
    }
  },
  "accessibility": {
    "requirements": [
      "WCAG AA contrast for text and interactive elements.",
      "Visible focus ring: use ring-2 ring-ring ring-offset-2 ring-offset-background.",
      "Keyboard navigation for wizard: Enter = Next when valid; Esc closes dialogs/drawers.",
      "Use aria-label for icon-only buttons (theme toggle, delete).",
      "Respect prefers-reduced-motion: reduce motion durations and disable parallax/noise if needed."
    ]
  },
  "libraries": {
    "required": [
      "framer-motion",
      "recharts",
      "lucide-react",
      "sonner",
      "jspdf"
    ],
    "optional": [
      "@radix-ui/react-icons (only if needed; prefer lucide-react)",
      "react-use (for debounced values)"
    ],
    "implementation_notes_js": [
      "This codebase uses .js files (not .tsx). Keep components in JS and use PropTypes only if already used elsewhere.",
      "All interactive and key informational elements must include data-testid attributes in kebab-case."
    ]
  },
  "image_urls": [
    {
      "category": "landing_hero_background",
      "description": "Subtle abstract teal/gray mesh used as a decorative background image behind hero (apply with low opacity + blur).",
      "url": "https://images.unsplash.com/photo-1656248396925-ec086a35c568?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwzfHxtaW5pbWFsJTIwYWJzdHJhY3QlMjBncmFkaWVudCUyMG1lc2glMjB0ZWFsJTIwZ3JheXxlbnwwfHx8dGVhbHwxNzc2OTY1NDc1fDA&ixlib=rb-4.1.0&q=85"
    },
    {
      "category": "landing_section_background_alt",
      "description": "Backup abstract blur background for secondary sections (use as masked corner glow).",
      "url": "https://images.unsplash.com/photo-1707209856577-eeea3627f8bf?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwxfHxtaW5pbWFsJTIwYWJzdHJhY3QlMjBncmFkaWVudCUyMG1lc2glMjB0ZWFsJTIwZ3JheXxlbnwwfHx8dGVhbHwxNzc2OTY1NDc1fDA&ixlib=rb-4.1.0&q=85"
    },
    {
      "category": "dashboard_texture",
      "description": "Linear-like subtle lines texture; use extremely low opacity as a background layer in results dashboard only.",
      "url": "https://images.unsplash.com/photo-1544185196-bd8bcb3bcca4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxtaW5pbWFsJTIwYWJzdHJhY3QlMjBncmFkaWVudCUyMG1lc2glMjB0ZWFsJTIwZ3JheXxlbnwwfHx8dGVhbHwxNzc2OTY1NDc1fDA&ixlib=rb-4.1.0&q=85"
    }
  ],
  "instructions_to_main_agent": {
    "global": [
      "Remove CRA default App.css centering patterns; do not use .App { text-align:center }.",
      "Implement theme toggle by toggling 'dark' class on <html> or <body> and persist in localStorage.",
      "Use the tokenized colors in index.css; avoid hard-coded hex except for charts if necessary.",
      "Use shadcn/ui components from /app/frontend/src/components/ui only for dropdowns, dialogs, calendar, etc.",
      "Add data-testid to: nav links, wizard inputs, next/back buttons, results cards, save/delete/export actions, error banners, empty states."
    ],
    "page_build_order": [
      "1) Landing page skeleton + nav",
      "2) Wizard stepper + progressive disclosure",
      "3) Loading analysis state",
      "4) Results dashboard (best option hero + ranked list + charts + compare + what-if)",
      "5) Saved decisions list + detail",
      "6) PDF export dialog"
    ],
    "recharts_style": [
      "Use muted gridlines: stroke='hsl(var(--border))' opacity 0.35.",
      "Tooltip: wrap in Card with bg-popover/80 + backdrop-blur.",
      "Animate bars on mount; keep duration ~280ms."
    ],
    "framer_motion_scaffold_js": {
      "snippet": "import { motion, AnimatePresence } from 'framer-motion';\n\nconst ease = [0.22, 1, 0.36, 1];\nconst stepVariants = {\n  initial: { opacity: 0, y: 12 },\n  animate: { opacity: 1, y: 0, transition: { duration: 0.26, ease } },\n  exit: { opacity: 0, y: -8, transition: { duration: 0.18, ease } },\n};\n\n// Usage:\n// <AnimatePresence mode=\"wait\">\n//   <motion.div key={stepId} variants={stepVariants} initial=\"initial\" animate=\"animate\" exit=\"exit\">...\n//   </motion.div>\n// </AnimatePresence>"
    }
  },
  "general_ui_ux_design_guidelines": [
    "- You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms",
    "- You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text",
    "- NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json",
    "\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**\n\n</Font Guidelines>\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead.\n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals."
  ]
}
