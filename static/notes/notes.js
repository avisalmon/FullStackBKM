// The Notes screen: a thin consumer of the REST API at /notes/api/notes/.
// No framework, no build step. Text is inserted with textContent, never innerHTML.
(function () {
  const API = "/notes/api/notes/";
  const csrf = document.body.dataset.csrf;
  const list = document.getElementById("notes-list");
  const form = document.getElementById("notes-form");
  const errorBox = document.getElementById("notes-error");

  async function api(url, options) {
    const response = await fetch(url, {
      credentials: "same-origin",
      ...options,
      headers: { "X-CSRFToken": csrf, Accept: "application/json", ...(options && options.headers) },
    });
    if (!response.ok) throw new Error("Request failed (" + response.status + ")");
    return response.status === 204 ? null : response.json();
  }

  function showError(error) {
    errorBox.textContent = error.message;
    errorBox.hidden = false;
  }

  function render(notes) {
    list.replaceChildren();
    if (!notes.length) {
      const empty = document.createElement("li");
      empty.textContent = "No notes yet.";
      list.append(empty);
      return;
    }
    for (const note of notes) {
      const item = document.createElement("li");
      const title = document.createElement("strong");
      title.textContent = note.title;
      item.append(title);
      if (note.body) item.append(" — " + note.body);
      if (note.image) {
        const img = document.createElement("img");
        img.src = note.image;
        img.alt = "";
        img.className = "notes-image";
        item.append(document.createElement("br"), img);
      }
      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "notes-quiet";
      remove.textContent = "Delete";
      remove.addEventListener("click", async () => {
        try {
          await api(API + note.id + "/", { method: "DELETE" });
          await load();
        } catch (error) {
          showError(error);
        }
      });
      item.append(" ", remove);
      list.append(item);
    }
  }

  async function load() {
    errorBox.hidden = true;
    render(await api(API));
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = new FormData(form);
    if (!data.get("image") || !data.get("image").size) data.delete("image");
    try {
      await api(API, { method: "POST", body: data });
      form.reset();
      await load();
    } catch (error) {
      showError(error);
    }
  });

  load().catch(showError);
})();
