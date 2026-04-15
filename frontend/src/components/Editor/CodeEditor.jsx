import Editor from '@monaco-editor/react';
import { useEffect, useRef } from 'react';
import useExecutionStore from '../../store/executionStore';

const CodeEditor = ({ code, onChange, errorLine, currentLine }) => {
  const editorRef = useRef(null);
  const monacoRef = useRef(null);
  const decorationsRef = useRef([]);
  const { breakpoints, toggleBreakpoint } = useExecutionStore();

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    editor.onMouseDown((e) => {
      if (e.target.type === 2) { // Glyph margin
        const line = e.target.position.lineNumber;
        toggleBreakpoint(line);
      }
    });
  };

  useEffect(() => {
    if (!editorRef.current || !monacoRef.current) return;

    const editor = editorRef.current;
    const monaco = monacoRef.current;

    const newDecorations = [];

    // Breakpoints
    Array.from(breakpoints).forEach((line) => {
      newDecorations.push({
        range: new monaco.Range(line, 1, line, 1),
        options: {
          isWholeLine: false,
          glyphMarginClassName: 'breakpoint-glyph',
          stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges
        }
      });
    });

    // Highlight error line
    if (errorLine > 0) {
      newDecorations.push({
        range: new monaco.Range(errorLine, 1, errorLine, 1),
        options: {
          isWholeLine: true,
          className: 'error-line',
          glyphMarginClassName: 'bg-red-500 w-1',
          marginClassName: 'bg-red-500/20'
        }
      });
    }

    // Highlight current execution line
    if (currentLine > 0 && !errorLine) {
      newDecorations.push({
        range: new monaco.Range(currentLine, 1, currentLine, 1),
        options: {
          isWholeLine: true,
          className: 'bg-indigo-900/30',
          glyphMarginClassName: 'bg-indigo-500 w-1'
        }
      });
    }

    decorationsRef.current = editor.deltaDecorations(decorationsRef.current, newDecorations);
  }, [errorLine, currentLine, breakpoints]);

  return (
    <div className="h-full w-full rounded-lg overflow-hidden border border-gray-800 relative">
      <style>{`
        .breakpoint-glyph {
          background: #ef4444;
          border-radius: 50%;
          width: 10px !important;
          height: 10px !important;
          margin-left: 5px;
          margin-top: 5px;
        }
      `}</style>
      <Editor
        height="100%"
        defaultLanguage="java"
        value={code}
        theme="vs-dark"
        onChange={onChange}
        onMount={handleEditorDidMount}
        options={{
          fontSize: 14,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          lineNumbers: 'on',
          automaticLayout: true,
          glyphMargin: true,
        }}
      />
    </div>
  );
};

export default CodeEditor;
