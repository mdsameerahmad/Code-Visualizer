import { motion } from 'framer-motion';

const ArrayVisualizer = ({ arrays = {}, prevArrays = {}, error = null }) => {

  console.log("ARRAY DATA:", arrays);

  if (!arrays || Object.keys(arrays).length === 0) {
    return (
      <div className="p-4 border border-yellow-500 text-yellow-400 rounded-lg">
        ⚠️ No array data found
      </div>
    );
  }

  return (
    <div className="space-y-6">

      {Object.entries(arrays).map(([name, data]) => {
        const values = data.values || [];
        const lastUpdatedIdx = data.lastUpdatedIndex;

        return (
          <div key={name} className="p-4 bg-gray-900 border border-gray-800 rounded-lg">

            <h3 className="text-sm text-gray-400 mb-4">
              Array: <span className="text-indigo-400">{name}</span>
            </h3>

            <div className="flex gap-3 items-end">

              {values.map((val, idx) => {

                const displayValue =
                  val === null || val === undefined || val === 0 ? '_' : val;

                const isUpdated = lastUpdatedIdx === idx;

                return (
                  <div key={idx} className="flex flex-col items-center">

                    <motion.div
                      animate={isUpdated ? { scale: [1, 1.2, 1] } : {}}
                      transition={{ duration: 0.4 }}
                      className={`w-14 h-14 flex items-center justify-center border-2 rounded font-mono text-lg
                        ${isUpdated ? 'border-green-500 bg-green-600/30' : 'border-gray-700 bg-gray-800'}
                      `}
                    >
                      {displayValue}
                    </motion.div>

                    <span className="text-xs text-gray-500 mt-1">{idx}</span>
                  </div>
                );
              })}

            </div>
          </div>
        );
      })}
    </div>
  );
};

export default ArrayVisualizer;