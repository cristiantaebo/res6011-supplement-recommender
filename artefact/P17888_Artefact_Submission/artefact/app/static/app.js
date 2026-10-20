"use strict";

const form = document.querySelector("#request-form");
const input = document.querySelector("#request-text");
const submitButton = document.querySelector("#submit-button");
const resetButton = document.querySelector("#reset-button");
const count = document.querySelector("#character-count");
const statusRegion = document.querySelector("#status");
const results = document.querySelector("#results");
const clarification = document.querySelector("#clarification");
const supportedGroups = document.querySelector("#supported-groups");

function setStatus(message, isError = false) {
  statusRegion.textContent = message;
  statusRegion.classList.toggle("error", isError);
}

function updateCount() {
  const remaining = 500 - input.value.length;
  count.textContent = `${remaining} character${remaining === 1 ? "" : "s"} remaining`;
  submitButton.disabled = input.value.trim().length === 0;
}

function appendControlledChoice(label) {
  input.value = `${input.value.trim()} ${label}`.trim().slice(0, 500);
  updateCount();
  input.focus();
}

function renderChoices(choices) {
  clarification.replaceChildren();
  if (!choices || choices.length === 0) {
    clarification.hidden = true;
    return;
  }
  const heading = document.createElement("h3");
  heading.textContent = "Choose a predefined option";
  clarification.append(heading);
  for (const choice of choices) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "chip";
    button.textContent = choice.label;
    button.addEventListener("click", () => appendControlledChoice(choice.label));
    clarification.append(button);
  }
  clarification.hidden = false;
}

function renderResults(items, dataVersion) {
  results.replaceChildren();
  items.forEach((item, index) => {
    const card = document.createElement("li");
    card.className = "result-card";
    const rank = document.createElement("p");
    rank.className = "rank-label";
    rank.textContent = index === 0 ? "Highest-scoring match" : `Rank ${index + 1}`;
    const heading = document.createElement("h3");
    heading.textContent = item.name;
    const score = document.createElement("p");
    score.className = "score";
    score.textContent = `Relevance score: ${item.score}`;
    const summary = document.createElement("p");
    summary.textContent = item.summary;
    const recommendation = document.createElement("p");
    recommendation.textContent = item.recommendation_text;
    const recipe = document.createElement("p");
    recipe.textContent = `Predefined use text: ${item.recipe_text}`;
    const details = document.createElement("details");
    const detailsTitle = document.createElement("summary");
    detailsTitle.textContent = "Why this matched";
    const reasonList = document.createElement("ul");
    reasonList.className = "reason-list";
    item.reasons.forEach((reason) => {
      const row = document.createElement("li");
      row.textContent = `${reason.label}: ${reason.points} points — ${reason.text}`;
      reasonList.append(row);
    });
    const version = document.createElement("p");
    version.textContent = `Controlled data/rule version: ${dataVersion}. Source reference retained in the database.`;
    details.append(detailsTitle, reasonList);
    card.append(rank, heading, score, summary, recommendation, recipe, details, version);
    results.append(card);
  });
}

async function submitRequest(event) {
  event.preventDefault();
  if (!input.value.trim()) {
    setStatus("Enter a supported non-medical goal before submitting.", true);
    input.focus();
    return;
  }
  submitButton.disabled = true;
  setStatus("Checking predefined data and rules…");
  results.replaceChildren();
  clarification.hidden = true;
  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({text: input.value})
    });
    const data = await response.json();
    if (!response.ok) {
      setStatus(data.message || "The request was not accepted.", true);
      return;
    }
    setStatus(data.message);
    renderChoices(data.choices || []);
    renderResults(data.recommendations || [], data.data_version || "unavailable");
  } catch (_) {
    setStatus("The local prototype is unavailable. Start it and try again.", true);
  } finally {
    updateCount();
  }
}

function resetInterface() {
  form.reset();
  results.replaceChildren();
  clarification.replaceChildren();
  clarification.hidden = true;
  setStatus("Ready for a supported request.");
  updateCount();
  input.focus();
}

async function loadTaxonomy() {
  try {
    const response = await fetch("/api/taxonomy");
    const data = await response.json();
    const grouped = {};
    for (const term of data.terms) {
      (grouped[term.category] ||= []).push(term);
    }
    const labels = {wellness_goal: "Wellness goals", preference: "Preferences", format: "Formats"};
    for (const category of ["wellness_goal", "preference", "format"]) {
      const group = document.createElement("div");
      group.className = "chip-group";
      const heading = document.createElement("h3");
      heading.textContent = labels[category];
      group.append(heading);
      for (const term of grouped[category] || []) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "chip";
        button.textContent = term.label;
        button.addEventListener("click", () => appendControlledChoice(term.label));
        group.append(button);
      }
      supportedGroups.append(group);
    }
  } catch (_) {
    setStatus("Supported choices could not be loaded from the local dataset.", true);
  }
}

input.addEventListener("input", updateCount);
form.addEventListener("submit", submitRequest);
resetButton.addEventListener("click", resetInterface);
updateCount();
loadTaxonomy();
