import type { Source } from '../types';

interface SourcesListProps {
  sources: Source[];
}

export function SourcesList({ sources }: SourcesListProps) {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="sources-list">
      <h4>Kaynaklar (Sources)</h4>
      <ul>
        {sources.map((source, index) => (
          <li key={source.chunk_id || index}>
            <strong>{source.doc_id}</strong> - Sayfa {source.page}
            <p className="excerpt">{source.excerpt}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
