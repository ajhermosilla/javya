import { useMemo } from 'react';
import type { MusicalKey } from '../types/song';
import { transposeChordPro, isChord } from '../utils/transpose';
import './ChordProViewer.css';

interface ChordProViewerProps {
  chordpro: string;
  fromKey: MusicalKey | null;
  toKey: MusicalKey;
}

/**
 * Renders a single line of ChordPro content.
 * Chords are displayed as styled spans, section headers are bold.
 */
function renderLine(line: string): React.ReactNode {
  const trimmed = line.trim();

  // Check if the entire line is a section header like [Verse 1]
  if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
    const content = trimmed.slice(1, -1);
    if (!isChord(content)) {
      return <div className="section-header">{content}</div>;
    }
  }

  // Check for ChordPro directives like {comment: text}
  const directiveMatch = trimmed.match(/^\{(\w+):\s*(.+)\}$/);
  if (directiveMatch) {
    const [, directive, value] = directiveMatch;
    if (directive.toLowerCase() === 'comment' || directive.toLowerCase() === 'c') {
      return <div className="chord-comment">{value}</div>;
    }
    if (directive.toLowerCase() === 'title') {
      return <div className="chord-directive-title">{value}</div>;
    }
    // Skip other directives
    return null;
  }

  // Empty line
  if (!trimmed) {
    return <div className="empty-line" />;
  }

  // Split line by chord annotations, keeping the brackets
  const parts = line.split(/(\[[^\]]+\])/);

  const elements: React.ReactNode[] = [];
  let keyIndex = 0;

  for (const part of parts) {
    if (!part) continue;

    if (part.startsWith('[') && part.endsWith(']')) {
      const content = part.slice(1, -1);
      if (isChord(content)) {
        elements.push(
          <span key={keyIndex++} className="chord">
            {content}
          </span>
        );
      } else {
        // Inline section header (rare but possible)
        elements.push(
          <span key={keyIndex++} className="inline-section">
            [{content}]
          </span>
        );
      }
    } else {
      // Lyric text - preserve whitespace
      elements.push(
        <span key={keyIndex++} className="lyric">
          {part}
        </span>
      );
    }
  }

  return <div className="chord-line">{elements}</div>;
}

export function ChordProViewer({ chordpro, fromKey, toKey }: ChordProViewerProps) {
  const transposedContent = useMemo(() => {
    if (!fromKey || fromKey === toKey) {
      return chordpro;
    }
    return transposeChordPro(chordpro, fromKey, toKey);
  }, [chordpro, fromKey, toKey]);

  if (!transposedContent) {
    return null;
  }

  const lines = transposedContent.split('\n');

  return (
    <div className="chordpro-viewer">
      {lines.map((line, index) => (
        <div key={index}>{renderLine(line)}</div>
      ))}
    </div>
  );
}
