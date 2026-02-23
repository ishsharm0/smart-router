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

const { route, getModel } = require("../lib/classifier");

const DEBUG = process.env.OPENCLAW_MODEL_ROUTER_DEBUG === "1";

module.exports = function register(api) {
  api.on("before_model_resolve", async (event) => {
    const decision = route(event);
    
    if (DEBUG) {
      const prompt = String(event?.prompt || "").slice(0, 100);
      console.log(`[ModelRouter] type=${decision.type} model=${decision.modelId} reason=${decision.reason} prompt="${prompt}..."`);
    }
    
    const model = getModel(decision.modelKey);
    
    return {
      providerOverride: model?.provider || "openrouter",
      modelOverride: decision.modelId,
    };
  });
};
