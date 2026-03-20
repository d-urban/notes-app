import html from "eslint-plugin-html";

export default [
  {
    files: ["**/*.html"],
    plugins: { html },
  },
  {
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "script",
      globals: {
        document: "readonly",
        window: "readonly",
        fetch: "readonly",
        console: "readonly",
        setTimeout: "readonly",
        clearTimeout: "readonly",
        confirm: "readonly",
        alert: "readonly",
        FormData: "readonly",
        Image: "readonly",
        FileReader: "readonly",
        URL: "readonly",
        Blob: "readonly",
        HTMLElement: "readonly",
        Event: "readonly",
        MutationObserver: "readonly",
      },
    },
    rules: {
      "no-unused-vars": ["warn", { varsIgnorePattern: "^(startEditById|deleteNote)$" }],
      "no-undef": "error",
      "no-redeclare": "error",
      eqeqeq: "warn",
      "no-var": "warn",
    },
  },
];
