const PYODIDE_VERSION = "314.0.6";
const PYODIDE_BASE = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;
let pyodidePromise: Promise<any> | null = null;

export async function getBrowserPython(): Promise<any> {
  if (pyodidePromise) return pyodidePromise;
  pyodidePromise = (async () => {
    if (typeof window === "undefined") throw new Error("Python runtime is browser-only.");
    if (!(window as any).loadPyodide) {
      const script = document.createElement("script");
      script.src = `${PYODIDE_BASE}pyodide.js`;
      script.async = true;
      document.head.appendChild(script);
      await new Promise<void>((resolve, reject) => {
        script.onload = () => resolve();
        script.onerror = () => reject(new Error("Pyodide could not be loaded from the CDN."));
      });
    }
    return (window as any).loadPyodide({ indexURL: PYODIDE_BASE });
  })();
  return pyodidePromise;
}

function assertLines(testCode: string): string[] {
  return (testCode || "").split(/\r?\n/).map((line) => line.trim()).filter((line) => line.startsWith("assert "));
}

export async function runPythonTests(code: string, testCode: string) {
  if (code.length > 512_000) throw new Error("Code is too large.");
  const pyodide = await getBrowserPython();
  const tests = assertLines(testCode);
  const details: Array<{ test: string; passed: boolean; output?: string; error?: string }> = [];

  let output = "";
  pyodide.setStdout({ batched: (text: string) => { output += text; } });
  pyodide.setStderr({ batched: (text: string) => { output += text; } });

  const run = async (assertion?: string) => {
    const assertionCode = assertion ? `\n${assertion}` : "";
    const wrapped = `__dsir_ns = {}\nexec(compile(${JSON.stringify(code)}, "<dsir>", "exec"), __dsir_ns)${assertionCode}\n`;
    await pyodide.runPythonAsync(wrapped);
  };

  if (!tests.length) {
    try {
      await run();
      details.push({ test: "Execution", passed: true, output: output || "(no output)" });
    } catch (error: any) {
      details.push({ test: "Execution", passed: false, output, error: String(error?.message || error) });
    }
  } else {
    for (let i = 0; i < tests.length; i++) {
      try {
        output = "";
        await run(tests[i]);
        details.push({ test: `Test ${i + 1}`, passed: true, output: output || "(no output)" });
      } catch (error: any) {
        details.push({ test: `Test ${i + 1}`, passed: false, output, error: String(error?.message || error) });
      }
    }
  }

  const passed = details.filter((item) => item.passed).length;
  const failed = details.length - passed;
  const firstError = details.find((item) => !item.passed)?.error;
  return { passed, failed, total: details.length, details, error: firstError || null };
}
