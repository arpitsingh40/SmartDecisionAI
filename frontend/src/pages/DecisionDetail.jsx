import React, { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

const DecisionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  useEffect(() => {
    navigate(`/results?id=${id}`, { replace: true });
  }, [id, navigate]);
  return null;
};

export default DecisionDetail;
