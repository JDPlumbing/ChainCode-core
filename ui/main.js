document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const output = document.querySelector("#output");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    output.innerText = "⏳ Generating chaincodes...";

    const formData = new FormData(form);
    const fields = {};
    let entity_type = "entity";
    let register = false;
    let download = false;

    // Gather inputs
    for (const [key, value] of formData.entries()) {
      if (key === "entity_type") {
        entity_type = value;
      } else if (key === "register") {
        register = true;
      } else if (key === "download") {
        download = true;
      } else if (key !== "visibility" && value.trim() !== "") {
        fields[key] = value.trim();
      }
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
      output.innerText = `✅ Generated entity and ${data.fields.length} fields\n\n` +
        JSON.stringify(data, null, 2);

      if (download && data.entity && data.entity.public_slug) {
        const slug = data.entity.public_slug;
        const downloadUrl = `/download/${slug}`;
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = `${slug}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      }
    } catch (err) {
      output.innerText = "❌ Error:\n\n" + err.message;
    }
  });
});
