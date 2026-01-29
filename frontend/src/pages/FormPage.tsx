import { useNavigate } from 'react-router-dom';
import { NoduleForm } from '../components/NoduleForm';
import { useEvaluationContext } from '../context/EvaluationContext';

export function FormPage() {
  const { evaluate, loading } = useEvaluationContext();
  const navigate = useNavigate();

  const handleSubmit = (data: Parameters<typeof evaluate>[0]) => {
    evaluate(data);
    navigate('/results');
  };

  return (
    <div className="form-container">
      <NoduleForm onSubmit={handleSubmit} loading={loading} />
    </div>
  );
}
