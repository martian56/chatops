import { useState, useRef, useEffect, useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';
import { commandsApi } from '../../api/commands';
import { Button } from '../ui/button';
import { Trash2, Copy, Check } from 'lucide-react';

interface TerminalProps {
  serverId: string;
}

interface CommandEntry {
  id: string;
  command: string;
  output: string;
  exitCode?: number;
  timestamp: Date;
  isError: boolean;
}

export const Terminal = ({ serverId }: TerminalProps) => {
  const [command, setCommand] = useState('');
  const [commandHistory, setCommandHistory] = useState<CommandEntry[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const terminalRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const historyRef = useRef<string[]>([]);

  const executeCommandMutation = useMutation({
    mutationFn: (cmd: string) => commandsApi.execute(serverId, cmd),
    onSuccess: (data, cmd) => {
      const entry: CommandEntry = {
        id: Date.now().toString(),
        command: cmd,
        output: data.output || '',
        exitCode: data.exit_code,
        timestamp: new Date(),
        isError: data.exit_code !== undefined && data.exit_code !== 0,
      };
      setCommandHistory((prev) => [...prev, entry]);
      historyRef.current = [cmd, ...historyRef.current.filter((c) => c !== cmd)].slice(0, 50);
      setHistoryIndex(-1);
      setCommand('');
    },
    onError: (error: any, cmd) => {
      const entry: CommandEntry = {
        id: Date.now().toString(),
        command: cmd,
        output: error?.response?.data?.detail || error.message || 'Command execution failed',
        exitCode: 1,
        timestamp: new Date(),
        isError: true,
      };
      setCommandHistory((prev) => [...prev, entry]);
      historyRef.current = [cmd, ...historyRef.current.filter((c) => c !== cmd)].slice(0, 50);
      setHistoryIndex(-1);
      setCommand('');
    },
  });

  // Auto-scroll to bottom when new output arrives or command changes
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [commandHistory, command]);

  // Focus input on mount and after command execution
  useEffect(() => {
    // Small delay to ensure DOM is updated
    const timer = setTimeout(() => {
      inputRef.current?.focus();
    }, 10);
    return () => clearTimeout(timer);
  }, [commandHistory]);

  const handleSpecialCommand = useCallback((cmd: string) => {
    const parts = cmd.split(' ');
    const command = parts[0].toLowerCase();

    switch (command) {
      case '/clear':
        setCommandHistory([]);
        break;
      case '/help':
        const helpEntry: CommandEntry = {
          id: Date.now().toString(),
          command: cmd,
          output: `Available commands:
/clear          - Clear the terminal
/help           - Show this help message
/history        - Show command history
/version        - Show agent version info`,
          exitCode: 0,
          timestamp: new Date(),
          isError: false,
        };
        setCommandHistory((prev) => [...prev, helpEntry]);
        break;
      case '/history':
        const historyText = historyRef.current.length > 0
          ? historyRef.current.slice(0, 20).join('\n')
          : 'No command history';
        const historyEntry: CommandEntry = {
          id: Date.now().toString(),
          command: cmd,
          output: historyText,
          exitCode: 0,
          timestamp: new Date(),
          isError: false,
        };
        setCommandHistory((prev) => [...prev, historyEntry]);
        break;
      case '/version':
        const versionEntry: CommandEntry = {
          id: Date.now().toString(),
          command: cmd,
          output: 'ChatOps Agent Terminal v1.0.0',
          exitCode: 0,
          timestamp: new Date(),
          isError: false,
        };
        setCommandHistory((prev) => [...prev, versionEntry]);
        break;
      default:
        const errorEntry: CommandEntry = {
          id: Date.now().toString(),
          command: cmd,
          output: `Unknown command: ${command}. Type /help for available commands.`,
          exitCode: 1,
          timestamp: new Date(),
          isError: true,
        };
        setCommandHistory((prev) => [...prev, errorEntry]);
    }
  }, []);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (!command.trim() || executeCommandMutation.isPending) {
        return;
      }

      const cmd = command.trim();

      // Handle special commands
      if (cmd.startsWith('/')) {
        handleSpecialCommand(cmd);
        setCommand('');
        // Focus will be handled by useEffect watching commandHistory
        return;
      }

      // Execute regular command
      executeCommandMutation.mutate(cmd);
    },
    [command, executeCommandMutation, handleSpecialCommand]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (historyRef.current.length > 0) {
          const newIndex = historyIndex < historyRef.current.length - 1 ? historyIndex + 1 : historyIndex;
          setHistoryIndex(newIndex);
          setCommand(historyRef.current[historyRef.current.length - 1 - newIndex] || '');
        }
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (historyIndex > 0) {
          const newIndex = historyIndex - 1;
          setHistoryIndex(newIndex);
          setCommand(historyRef.current[historyRef.current.length - 1 - newIndex] || '');
        } else if (historyIndex === 0) {
          setHistoryIndex(-1);
          setCommand('');
        }
      } else if (e.key === 'Escape') {
        setCommand('');
        setHistoryIndex(-1);
      }
    },
    [historyIndex]
  );

  const handleClear = useCallback(() => {
    setCommandHistory([]);
  }, []);

  const handleCopy = useCallback(async (id: string, text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  }, []);

  const getPrompt = () => {
    return `$`;
  };

  return (
    <div className="flex flex-col h-full">
      {/* Terminal Header */}
      <div className="flex items-center justify-between mb-2 px-1">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <div className="flex gap-1">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
          </div>
          <span className="ml-2">Terminal</span>
        </div>
        <Button variant="ghost" size="sm" onClick={handleClear} className="h-7">
          <Trash2 className="h-4 w-4 mr-2" />
          Clear
        </Button>
      </div>

      {/* Terminal Output with Inline Input */}
      <div
        ref={terminalRef}
        className="flex-1 bg-black rounded-lg p-4 font-mono text-sm overflow-y-auto custom-scrollbar min-h-[400px] max-h-[600px]"
        style={{ fontFamily: 'Consolas, Monaco, "Courier New", monospace' }}
        onClick={() => inputRef.current?.focus()}
      >
        {commandHistory.length === 0 ? (
          <div className="text-green-400">
            <div className="mb-4 text-muted-foreground">
              <span className="text-blue-400">ChatOps Terminal</span> • Type <span className="text-green-400">/help</span> for commands
            </div>
            <form onSubmit={handleSubmit} className="flex items-center gap-2">
              <span className="text-green-400 select-none">{getPrompt()}</span>
              <input
                ref={inputRef}
                type="text"
                value={command}
                onChange={(e) => {
                  setCommand(e.target.value);
                  setHistoryIndex(-1);
                }}
                onKeyDown={handleKeyDown}
                placeholder=""
                disabled={executeCommandMutation.isPending}
                className="flex-1 bg-transparent text-green-400 outline-none placeholder:text-muted-foreground/50"
                autoComplete="off"
                spellCheck="false"
                style={{ caretColor: '#22c55e' }}
              />
              {executeCommandMutation.isPending && (
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              )}
            </form>
          </div>
        ) : (
          <div className="space-y-1">
            {commandHistory.map((entry) => (
              <div key={entry.id} className="mb-3 group">
                {/* Command */}
                <div className="flex items-start gap-2 mb-1">
                  <span className="text-green-400 select-none">{getPrompt()}</span>
                  <span className="text-foreground flex-1">{entry.command}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => handleCopy(entry.id, entry.output)}
                    title="Copy output"
                  >
                    {copiedId === entry.id ? (
                      <Check className="h-3 w-3 text-green-400" />
                    ) : (
                      <Copy className="h-3 w-3 text-muted-foreground" />
                    )}
                  </Button>
                </div>
                {/* Output */}
                <div
                  className={`ml-6 whitespace-pre-wrap break-words ${
                    entry.isError ? 'text-red-400' : 'text-green-400'
                  }`}
                >
                  {entry.output || '(no output)'}
                </div>
                {entry.exitCode !== undefined && (
                  <div className="ml-6 text-xs text-muted-foreground mt-1">
                    [Exit code: {entry.exitCode}]
                  </div>
                )}
              </div>
            ))}
            {/* Inline Command Input */}
            <form onSubmit={handleSubmit} className="flex items-center gap-2 mt-2">
              <span className="text-green-400 select-none">{getPrompt()}</span>
              <input
                ref={inputRef}
                type="text"
                value={command}
                onChange={(e) => {
                  setCommand(e.target.value);
                  setHistoryIndex(-1);
                }}
                onKeyDown={handleKeyDown}
                placeholder=""
                disabled={executeCommandMutation.isPending}
                className="flex-1 bg-transparent text-green-400 outline-none placeholder:text-muted-foreground/50"
                autoComplete="off"
                spellCheck="false"
                style={{ caretColor: '#22c55e' }}
              />
              {executeCommandMutation.isPending && (
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              )}
            </form>
          </div>
        )}
      </div>

      {/* Keyboard shortcuts hint */}
      <div className="text-xs text-muted-foreground mt-2 px-2">
        <kbd className="px-1.5 py-0.5 bg-muted rounded text-xs">↑</kbd>
        <kbd className="px-1.5 py-0.5 bg-muted rounded text-xs ml-1">↓</kbd> Navigate history •{' '}
        <kbd className="px-1.5 py-0.5 bg-muted rounded text-xs">Esc</kbd> Clear input •{' '}
        <span className="text-green-400">/clear</span> Clear terminal •{' '}
        <span className="text-green-400">/help</span> Show help
      </div>
    </div>
  );
};

