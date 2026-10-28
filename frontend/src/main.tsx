import React from "react";
import ReactDOM from "react-dom/client";
import { LanguageProvider } from "@suite/i18n";
import App from "./App";
import { translations } from "./i18n/translations";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <LanguageProvider translations={translations} defaultLanguage="it">
      <App />
    </LanguageProvider>
  </React.StrictMode>,
);
