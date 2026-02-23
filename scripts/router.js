/**
 * Skill-side classifier for model-router-intelligent.
 * Mirrors extension logic for local testing/dry-runs.
 * 
 * Usage:
 *   node router.js "your prompt here"
 *   node router.js --interactive
 */

const { route, classify, getModels, getModel } = require("../lib/classifier");
const readline = require("readline");

const DEBUG = process.env.OPENCLAW_MODEL_ROUTER_DEBUG === "1";

function main() {
  const args = process.argv.slice(2);
  
  if (args.includes("--interactive") || args.includes("-i")) {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });
    
    const prompt = () => {
      rl.question("prompt> ", (input) => {
        if (input.trim() === "exit" || input.trim() === "quit") {
          rl.close();
          return;
        }
        if (input.trim()) {
          const result = route({ prompt: input });
          console.log(JSON.stringify(result, null, 2));
        }
        prompt();
      });
    };
    
    prompt();
    return;
  }
  
  if (args.includes("--list") || args.includes("-l")) {
    const models = getModels();
    console.log("Available models:");
    for (const [key, model] of Object.entries(models)) {
      console.log(`  ${key}: ${model.id}`);
      console.log(`    aliases: ${model.aliases?.join(", ") || "none"}`);
      console.log(`    cost: $${model.cost.input}/$${model.cost.output} (${model.cost.unit})`);
      console.log(`    context: ${model.context.toLocaleString()}`);
      console.log();
    }
    return;
  }
  
  if (args.includes("--help") || args.includes("-h")) {
    console.log(`Usage: node router.js [options] [prompt]
Options:
  -i, --interactive    Interactive mode
  -l, --list          List available models
  -h, --help          Show this help
`);
    return;
  }
  
  const prompt = args.join(" ");
  if (!prompt) {
    console.error("Usage: node router.js <prompt>");
    console.error("Try: node router.js --help");
    process.exit(1);
  }
  
  const result = route({ prompt });
  console.log(JSON.stringify(result, null, 2));
}

if (require.main === module) {
  main();
}

module.exports = { route, classify, getModels, getModel };
