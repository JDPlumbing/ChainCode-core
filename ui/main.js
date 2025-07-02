document.getElementById("chaincode-form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = new FormData(e.target);
  const data = {};
  formData.forEach((value, key) => {
    if (value) data[key] = value; // skip empty fields
  });

  const response = await fetch("/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  const result = await response.json();
  const output = document.getElementById("output");
  output.innerHTML = "<pre>" + JSON.stringify(result, null, 2) + "</pre>";
});
