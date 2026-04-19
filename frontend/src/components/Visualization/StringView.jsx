import { motion } from 'framer-motion';

const resolveIndexToken = (token, variables) => {
  if (!token) return null;
  const trimmed = token.trim();
  if (/^-?\d+$/.test(trimmed)) return parseInt(trimmed, 10);
  const v = variables?.[trimmed];
  return Number.isInteger(v) ? v : null;
};

const extractStringOp = (step, variables) => {
  const line = step?.line_content || '';
  const charAt = line.match(/(\w+)\.charAt\(([^)]+)\)/);
  if (charAt) {
    return {
      type: 'charAt',
      name: charAt[1],
      index: resolveIndexToken(charAt[2], variables),
    };
  }

  const substring = line.match(/(\w+)\.substring\(([^)]+)\)/);
  if (substring) {
    const args = substring[2].split(',').map((a) => a.trim());
    return {
      type: 'substring',
      name: substring[1],
      start: resolveIndexToken(args[0], variables),
      end: args[1] ? resolveIndexToken(args[1], variables) : null,
    };
  }

  return null;
};

const StringView = ({ step }) => {
  const variables = step?.variables || {};
  const strings = Object.entries(variables).filter(([, value]) => typeof value === 'string');
  if (strings.length === 0) return null;

  const op = extractStringOp(step, variables);

  return (
    <div className="p-4 bg-gray-900 rounded-lg border border-gray-800 border-l-4 border-l-cyan-600">
      <h3 className="text-sm font-bold text-gray-300 uppercase tracking-widest mb-3">Strings</h3>
      <div className="space-y-4">
        {strings.map(([name, value]) => {
          const chars = [...value];
          const active = op && op.name === name ? op : null;
          return (
            <div key={name} className="p-3 bg-gray-950/60 border border-gray-800 rounded">
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-cyan-300">{name}</span>
                <span className="text-xs text-gray-500 font-mono">length = {chars.length}</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {chars.map((ch, idx) => {
                  const isCharAt = active?.type === 'charAt' && active.index === idx;
                  const inRange =
                    active?.type === 'substring' &&
                    active.start !== null &&
                    idx >= active.start &&
                    (active.end === null || idx < active.end);
                  return (
                    <motion.div
                      key={`${name}-${idx}`}
                      layout
                      className={`w-8 h-8 rounded border text-xs font-mono flex items-center justify-center ${
                        isCharAt
                          ? 'bg-cyan-800/50 border-cyan-400 text-cyan-100'
                          : inRange
                          ? 'bg-violet-800/40 border-violet-400 text-violet-100'
                          : 'bg-gray-800 border-gray-700 text-gray-200'
                      }`}
                    >
                      {ch === ' ' ? '[sp]' : ch}
                    </motion.div>
                  );
                })}
              </div>
              {active?.type === 'charAt' && active.index !== null && (
                <div className="mt-2 text-xs text-cyan-300 font-mono">charAt index: {active.index}</div>
              )}
              {active?.type === 'substring' && active.start !== null && (
                <div className="mt-2 text-xs text-violet-300 font-mono">
                  substring range: {active.start}..{active.end ?? chars.length}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default StringView;
