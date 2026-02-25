/**
 * Intelligent model router plugin for OpenClaw.
 * 
 * Installs to: ~/.openclaw/extensions/model-router/
 * Requires: config/models.json, config/categories.json, lib/classifier.js
 * 
 * Config in openclaw.json:
 * {
 *   "plugins": {
 *     "allow": ["model-router"],
 *     "entries": {
 *       "model-router": { "enabled": true }
 *     }
 *   }
 * }
 */

function loadClassifier() {
  try {
    return require("./lib/classifier");
  } catch {
    // Supports symlinked installs where index.js points into workspace/skills/*/extension.
    return require("../lib/classifier");
  }
}

const { route, getModel } = loadClassifier();
const DEBUG = process.env.OPENCLAW_MODEL_ROUTER_DEBUG === "1";

function getPromptText(event) {
  const candidates = [];

  for (const key of ["message", "userMessage", "input", "inputText", "promptText"]) {
    if (typeof event?.[key] === "string" && event[key].trim()) {
      candidates.push(event[key].trim());
    }
  }

  if (Array.isArray(event?.messages)) {
    for (let i = event.messages.length - 1; i >= 0; i -= 1) {
      const msg = event.messages[i];
      if (!msg || msg.role !== "user") continue;
      if (typeof msg.content === "string" && msg.content.trim()) {
        candidates.push(msg.content.trim());
        break;
      }
      if (Array.isArray(msg.content)) {
        const text = msg.content
          .map((part) => (typeof part?.text === "string" ? part.text : ""))
          .filter(Boolean)
          .join("\n")
          .trim();
        if (text) {
          candidates.push(text);
          break;
        }
      }
    }
  }

  const raw = String(event?.prompt || "");
  const stripped = raw.replace(/^Conversation info[\s\S]*?\n\n/, "");
  const userBlocks = [...stripped.matchAll(/(?:^|\n)user\s*:\s*([\s\S]*?)(?=\n(?:assistant|system|tool)\s*:|$)/gi)];
  if (userBlocks.length) {
    const lastUser = userBlocks[userBlocks.length - 1][1]?.trim();
    if (lastUser) candidates.push(lastUser);
  }

  const nonEmptyLines = stripped
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  if (nonEmptyLines.length) {
    candidates.push(nonEmptyLines[nonEmptyLines.length - 1]);
  }

  const chosen = candidates.find((c) => c && c.length > 0) || stripped || raw;
  return chosen.slice(-4000);
}

module.exports = function register(api) {
  api.on("before_model_resolve", async (event) => {
    try {
      const prompt = getPromptText(event);
      const decision = route({ prompt });
      const model = getModel(decision.modelKey);

      if (DEBUG) {
        const preview = prompt.slice(0, 120).replace(/\s+/g, " ").trim();
        console.log(
          `[ModelRouter] type=${decision.type} model=${decision.modelId} reason=${decision.reason} prompt="${preview}"`
        );
      }

      return {
        providerOverride: model?.provider || "openrouter",
        modelOverride: decision.modelId,
      };
    } catch (err) {
      if (DEBUG) {
        console.log(`[ModelRouter] error=${err?.message || String(err)}`);
      }
      return undefined;
    }
  });
};
