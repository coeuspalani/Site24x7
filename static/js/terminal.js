const log = document.getElementById("terminalLog");
const apiList = document.getElementById("apiList");
const modal = document.getElementById("modal");
const modalContent = document.getElementById("modalContent");
document.getElementById("apiSearch").addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase();

    const filtered = allApis.filter(api =>
        api.method.toLowerCase().includes(query) ||
        api.path.toLowerCase().includes(query)
    );

    renderApiList(filtered);
});

document.getElementById("runBtn").onclick = async () => {
    const payload = {
        path: document.getElementById("path").value,
        method: document.getElementById("method").value,
        tag: document.getElementById("tag").value,
        summary: document.getElementById("summary").value,
        operation_id: document.getElementById("operation_id").value,
        root_template: document.getElementById("root_template").value,
        xml_file: document.getElementById("xml_file").value,
        output: document.getElementById("output").value
    };

    log.textContent = "Running yamlcon...";

    try {
        const res = await fetch("/convert", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        log.textContent = data.message || data.error;
        loadApis();
    } catch {
        log.textContent = "Error executing command";
    }
};

let allApis = [];

async function loadApis() {
    apiList.innerHTML = "";
    const res = await fetch("/available-paths");
    allApis = await res.json();

    renderApiList(allApis);
}
function renderApiList(apis) {
    apiList.innerHTML = "";

    apis.forEach(api => {
        const li = document.createElement("li");

        li.innerHTML = `
            <div class="api-row">
                <span class="api-method">${api.method}</span>
                <span class="api-path">${api.path}</span>
            </div>
        `;

        const pathEl = li.querySelector(".api-path");

        pathEl.addEventListener("click", (e) => {
            e.stopPropagation();
            pathEl.classList.toggle("expanded");
        });

        li.addEventListener("click", () => {
            loadSample(api.path, api.method);
        });

        apiList.appendChild(li);
    });
}


async function loadSample(path, method) {
    modal.style.display = "flex";
    modalContent.textContent = "Generating sample...";

    const res = await fetch("/sample-response", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path, method })
    });

    const data = await res.json();

    modalContent.textContent = JSON.stringify(data, null, 2);
}


function closeModal() {
    modal.style.display = "none";
}
function addApiItem(method, path) {
  const li = document.createElement("li");

  li.innerHTML = `
    <div class="api-row">
      <span class="api-method">${method}</span>
      <span class="api-path">${path}</span>
    </div>
  `;

  const pathEl = li.querySelector(".api-path");

  li.addEventListener("click", () => {
    pathEl.classList.toggle("expanded");
  });

  document.getElementById("apiList").appendChild(li);
}

loadApis();
