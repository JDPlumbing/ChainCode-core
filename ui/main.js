// Updated main.js rendering logic

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const output = document.querySelector("#output");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    output.innerHTML = "<p>⏳ Generating chaincodes...</p>";

    const formData = new FormData(form);
    const fields = {};
    let entity_type = "entity";
    let register = false;
    let download = false;

    for (const [key, value] of formData.entries()) {
      if (key === "entity_type") entity_type = value;
      else if (key === "register") register = true;
      else if (key === "download") download = true;
      else if (key !== "visibility" && value.trim() !== "") fields[key] = value.trim();
    }

    const payload = {
      entity_type,
      fields,
      register,
      download
    };

    try {
      const res = await fetch("/generate_entity", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      const { entity, fields: fieldResults, links } = data;

      const html = [
        `<div class="card">`,
        `<h3>✅ Chaincode Generated</h3>`,
        `<p><strong>Entity Type:</strong> ${entity.metadata.type}</p>`,
        `<p><strong>Slug:</strong> <code>${entity.public_slug}</code></p>`,
        `<p><strong>Visibility:</strong> ${entity.metadata.visibility}</p>`,
        `<p><strong>Chaincode ID:</strong> <code>${entity.chaincode_id}</code></p>`,

        `<h4>🔗 Linked Fields:</h4>`,
        `<ul>` + fieldResults.map(f => `<li><strong>${f.metadata.type}:</strong> ${f.metadata.value}</li>`).join("") + `</ul>`,

        `<h4>🔐 Links:</h4>`,
        `<ul>` + links.map(link => `<li><code>${link.from_id.slice(0,12)}</code> → <code>${link.to_id.slice(0,12)}</code> (${link.link_type})</li>`).join("") + `</ul>`,

        `<details><summary>📦 Raw JSON Output</summary><pre>${JSON.stringify(data, null, 2)}</pre></details>`,
        `</div>`
      ];

      output.innerHTML = html.join("");

      if (download && entity.public_slug) {
        const slug = entity.public_slug;
        const downloadUrl = `/download/${slug}`;
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = `${slug}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      }
    } catch (err) {
      output.innerHTML = `<p style="color:red;">❌ Error:<br><br>${err.message}</p>`;
    }
  });
});
