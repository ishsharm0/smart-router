/**
 * Core classifier library - shared between extension and skill scripts.
 * Config-driven routing logic for maximum modularity.
 */

const fs = require("fs");
const path = require("path");

// Resolve skill directory relative to this file
const SKILL_DIR = path.resolve(__dirname, "..");
const CONFIG_DIR = path.join(SKILL_DIR, "config");

// Load configs
let modelsConfig = {};
let categoriesConfig = {};

function loadConfigs() {
  try {
    modelsConfig = JSON.parse(fs.readFileSync(path.join(CONFIG_DIR, "models.json"), "utf8"));
    categoriesConfig = JSON.parse(fs.readFileSync(path.join(CONFIG_DIR, "categories.json"), "utf8"));
  } catch (e) {
    console.error("[ModelRouter] Failed to load configs:", e.message);
  }
}

loadConfigs();

/**
 * Get all enabled models from config
 */
function getModels() {
  const models = {};
  for (const [key, model] of Object.entries(modelsConfig.models || {})) {
    if (model.enabled !== false) {
      models[key] = model;
    }
  }
  return models;
}

/**
 * Resolve model key from alias
 */
function resolveModelFromAlias(alias) {
  const models = getModels();
  const lower = String(alias || "").trim().toLowerCase();
  
  for (const [key, model] of Object.entries(models)) {
    if (model.aliases?.some(a => a.toLowerCase() === lower)) {
      return { key, ...model };
    }
  }
  return null;
}

/**
 * Get model config by key or resolve from alias
 */
function getModel(modelKey) {
  const models = getModels();
  if (models[modelKey]) {
    return { key: modelKey, ...models[modelKey] };
  }
  // Try resolving as alias
  return resolveModelFromAlias(modelKey);
}

/**
 * Check if text matches any keyword (case-insensitive)
 */
function containsAny(text, keywords) {
  if (!keywords || !Array.isArray(keywords)) return false;
  const lower = String(text || "").toLowerCase();
  return keywords.some(kw => lower.includes(kw.toLowerCase()));
}

/**
 * Check if text matches any regex pattern
 */
function matchesAnyPattern(text, patterns) {
  if (!patterns || !Array.isArray(patterns)) return false;
  const str = String(text || "");
  return patterns.some(pattern => {
    try {
      return new RegExp(pattern, "i").test(str);
    } catch {
      return false;
    }
  });
}

/**
 * Calculate prompt metrics
 */
function analyzePrompt(text) {
  const str = String(text || "");
  return {
    text: str,
    lower: str.toLowerCase(),
    words: str.split(/\s+/).filter(Boolean),
    estimatedTokens: Math.ceil(str.length / 4),
    codeFenceCount: (str.match(/```[\s\S]*?```/g) || []).length,
    filePathCount: (str.match(/\b[a-z0-9_\-/]+\.(ts|tsx|js|jsx|py|go|rs|json|ya?ml|md|sql|sh|html|css)\b/gi) || []).length,
  };
}

/**
 * Check if a category's thresholds are met
 */
function checkThresholds(metrics, thresholds) {
  if (!thresholds) return false;
  
  const checks = [
    ["minCodeFences", (t, m) => m.codeFenceCount >= t],
    ["minFilePaths", (t, m) => m.filePathCount >= t],
    ["minTokens", (t, m) => m.estimatedTokens >= t],
    ["minWords", (t, m) => m.words.length >= t],
    ["maxWords", (t, m) => m.words.length <= t],
    ["maxTokens", (t, m) => m.estimatedTokens <= t],
  ];
  
  return checks.every(([key, fn]) => {
    if (thresholds[key] === undefined) return true;
    return fn(thresholds[key], metrics);
  });
}

/**
 * Classify a prompt against categories (priority order)
 */
function classify(prompt) {
  const metrics = analyzePrompt(prompt);
  const categories = categoriesConfig.categories || {};
  const fallback = categoriesConfig.fallback || { model: "minimax" };
  
  // Sort categories by priority (higher first)
  const sortedCategories = Object.entries(categories)
    .sort((a, b) => (b[1].priority || 0) - (a[1].priority || 0));
  
  for (const [categoryKey, category] of sortedCategories) {
    const triggers = category.triggers || {};
    
    // Check keywords
    if (triggers.keywords && containsAny(metrics.lower, triggers.keywords)) {
      const model = getModel(category.model);
      return {
        category: categoryKey,
        modelKey: category.model,
        modelId: model?.id || category.model,
        reason: `${categoryKey}_keyword`,
        enableThinking: category.enableThinking || false,
        metrics,
      };
    }
    
    // Check patterns
    if (triggers.patterns && matchesAnyPattern(metrics.text, triggers.patterns)) {
      const model = getModel(category.model);
      return {
        category: categoryKey,
        modelKey: category.model,
        modelId: model?.id || category.model,
        reason: `${categoryKey}_pattern`,
        enableThinking: category.enableThinking || false,
        metrics,
      };
    }
    
    // Check thresholds
    if (triggers.thresholds && checkThresholds(metrics, triggers.thresholds)) {
      const model = getModel(category.model);
      return {
        category: categoryKey,
        modelKey: category.model,
        modelId: model?.id || category.model,
        reason: `${categoryKey}_threshold`,
        enableThinking: category.enableThinking || false,
        metrics,
      };
    }
  }
  
  // Fallback
  const model = getModel(fallback.model);
  return {
    category: "default",
    modelKey: fallback.model,
    modelId: model?.id || fallback.model,
    reason: "fallback",
    enableThinking: false,
    metrics,
  };
}

/**
 * Resolve explicit model override from prompt or event
 */
function resolveExplicitOverride(input) {
  const prompt = String(input?.prompt || input?.promptText || "");
  const models = getModels();
  
  // Check for --model flag in prompt
  const match = prompt.match(/(?:^|\s)(?:--model|model)\s*=?\s*([a-z0-9._\/-]+)/i);
  if (match && match[1]) {
    const resolved = getModel(match[1]);
    if (resolved) return resolved;
  }
  
  // Check event.model
  if (input?.model) {
    const resolved = getModel(input.model);
    if (resolved) return resolved;
  }
  
  // Check event.metadata?.model
  if (input?.metadata?.model) {
    const resolved = getModel(input.metadata.model);
    if (resolved) return resolved;
  }
  
  return null;
}

/**
 * Main routing decision
 */
function route(input) {
  const explicit = resolveExplicitOverride(input);
  const prompt = input?.prompt || input?.promptText || "";
  const classification = classify(prompt);
  
  if (explicit) {
    return {
      type: "explicit",
      modelKey: explicit.key,
      modelId: explicit.id,
      reason: "explicit_override",
      classification,
    };
  }
  
  return {
    type: classification.category,
    modelKey: classification.modelKey,
    modelId: classification.modelId,
    reason: classification.reason,
    enableThinking: classification.enableThinking,
  };
}

module.exports = {
  loadConfigs,
  getModels,
  getModel,
  resolveModelFromAlias,
  classify,
  resolveExplicitOverride,
  route,
  analyzePrompt,
  containsAny,
  matchesAnyPattern,
};
