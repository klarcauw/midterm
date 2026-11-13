
const API = "http://127.0.0.1:8000/api";

let token = localStorage.getItem("token");
let currentUser = null;
let editingArticleId = null;

const loginPage = document.getElementById("loginPage");
const dashboardPage = document.getElementById("dashboardPage");
const content = document.getElementById("content");

async function api(url, method = "GET", data = null) {
    const options = {
        method,
        headers: {}
    };

    if (token) {
        options.headers["Authorization"] = `Bearer ${token}`;
    }

    if (data !== null) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(data);
    }

    const response = await fetch(API + url, options);

    const result = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(result.detail || "Request failed");
    }

    return result;
}

function getArticleId(article) {
    return article.article_id ?? article.id;
}

function showMessage(message) {
    alert(message);
}

// LOGIN
document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    try {
        const response = await fetch(API + "/users/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Login failed");
        }

        token = result.access_token;
        localStorage.setItem("token", token);

        await loadUser();

    } catch (error) {
        document.getElementById("loginMessage").textContent = error.message;
    }
});

// GET CURRENT USER
async function loadUser() {
    try {
        currentUser = await api("/users/me");

        loginPage.classList.add("hidden");
        dashboardPage.classList.remove("hidden");

        document.getElementById("roleLabel").textContent =
            "Role: " + currentUser.role;

        if (currentUser.role === "author") {
            showAuthorDashboard();
        } else if (currentUser.role === "editor") {
            showEditorDashboard();
        } else {
            throw new Error("Unknown user role");
        }

    } catch (error) {
        logout();
        showMessage(error.message);
    }
}

// AUTHOR DASHBOARD
async function showAuthorDashboard() {
    content.innerHTML = `
        <h1>Author Dashboard</h1>

        <div class="card">
            <h2>My Submissions</h2>
            <button onclick="showArticleForm()">+ New Article</button>
            <div id="articleList">Loading...</div>
        </div>
    `;

    await loadMyArticles();
}

// LOAD AUTHOR ARTICLES
async function loadMyArticles() {
    try {
        const articles = await api("/articles/my");

        let html = `
            <table>
                <tr>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
        `;

        articles.forEach(article => {
            const id = getArticleId(article);

            html += `
                <tr>
                    <td>${escapeHTML(article.title)}</td>
                    <td>${escapeHTML(article.category_name ?? article.category?.name ?? article.category_id ?? "-")}</td>
                    <td class="status ${article.status}">
                        ${article.status}
                    </td>
                    <td>
                        ${
                            article.status === "editing"
                            ? `
                                <button onclick="editArticle(${id})">Edit</button>
                                <button class="success" onclick="submitArticle(${id})">Submit</button>
                                <button class="danger" onclick="deleteArticle(${id})">Delete</button>
                            `
                            : "-"
                        }
                    </td>
                </tr>
            `;
        });

        html += "</table>";

        document.getElementById("articleList").innerHTML =
            articles.length ? html : "<p>No submissions yet.</p>";

    } catch (error) {
        showMessage(error.message);
    }
}

// ARTICLE FORM
function showArticleForm(article = null) {
    editingArticleId = article ? getArticleId(article) : null;

    content.innerHTML = `
        <h1>${article ? "Edit Article" : "Create Article"}</h1>

        <div class="card">
            <form id="articleForm">
                <label>Title</label>
                <input id="articleTitle" required
                    value="${escapeHTML(article?.title ?? "")}">

                <label>Category</label>
                <select id="categoryId" required>
                    <option value="">Select Category</option>
                    <option value="1">Technology</option>
                    <option value="2">Education</option>
                    <option value="3">Lifestyle</option>
                    <option value="4">Business</option>
                    <option value="5">Science</option>
                </select>

                <label>Content</label>
                <textarea id="articleContent" required>${escapeHTML(article?.content ?? "")}</textarea>

                <button type="submit">Save Article</button>
                <button type="button" class="secondary"
                    onclick="showAuthorDashboard()">Cancel</button>
            </form>
        </div>
    `;

    if (article) {
        document.getElementById("categoryId").value =
            article.category_id;
    }

    document.getElementById("articleForm").addEventListener("submit", saveArticle);
}

async function saveArticle(e) {
    e.preventDefault();

    const data = {
        title: document.getElementById("articleTitle").value,
        content: document.getElementById("articleContent").value,
        category_id: Number(document.getElementById("categoryId").value)
    };

    try {
        if (editingArticleId) {
            await api(`/articles/${editingArticleId}`, "PUT", data);
        } else {
            await api("/articles/", "POST", data);
        }

        showMessage("Article saved successfully!");
        showAuthorDashboard();

    } catch (error) {
        showMessage(error.message);
    }
}

// EDIT ARTICLE
async function editArticle(id) {
    try {
        const articles = await api("/articles/my");
        const article = articles.find(a => getArticleId(a) == id);

        if (!article) {
            throw new Error("Article not found");
        }

        showArticleForm(article);

    } catch (error) {
        showMessage(error.message);
    }
}

// DELETE ARTICLE
async function deleteArticle(id) {
    if (!confirm("Delete this article?")) return;

    try {
        await api(`/articles/${id}`, "DELETE");
        showMessage("Article deleted!");
        showAuthorDashboard();

    } catch (error) {
        showMessage(error.message);
    }
}

// SUBMIT ARTICLE
async function submitArticle(id) {
    if (!confirm("Submit this article for review?")) return;

    try {
        await api(`/articles/${id}/submit`, "POST");
        showMessage("Article submitted!");
        showAuthorDashboard();

    } catch (error) {
        showMessage(error.message);
    }
}

// EDITOR DASHBOARD
async function showEditorDashboard() {
    content.innerHTML = `
        <h1>Editor Dashboard</h1>

        <div class="card">
            <h2>Pending Reviews</h2>
            <div id="reviewList">Loading...</div>
        </div>
    `;

    await loadReviews();
}

// LOAD PENDING REVIEWS
async function loadReviews() {
    try {
        const articles = await api("/editor/reviews/");

        let html = `
            <table>
                <tr>
                    <th>Author</th>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Action</th>
                </tr>
        `;

        articles.forEach(article => {
            const id = getArticleId(article);

            html += `
                <tr>
                    <td>${escapeHTML(article.author_username ?? article.author?.username ?? "-")}</td>
                    <td>${escapeHTML(article.title)}</td>
                    <td>${escapeHTML(article.category_name ?? article.category?.name ?? article.category_id ?? "-")}</td>
                    <td>
                        <button onclick="viewReview(${id})">Review</button>
                    </td>
                </tr>
            `;
        });

        html += "</table>";

        document.getElementById("reviewList").innerHTML =
            articles.length ? html : "<p>No pending reviews.</p>";

    } catch (error) {
        showMessage(error.message);
    }
}

// VIEW ARTICLE
async function viewReview(id) {
    try {
        const article = await api(`/editor/reviews/${id}`);

        content.innerHTML = `
            <h1>Review Article</h1>

            <div class="card">
                <h2>${escapeHTML(article.title)}</h2>
                <p>Author: ${escapeHTML(article.author_username ?? article.author?.username ?? "-")}</p>
                <p>Category: ${escapeHTML(article.category_name ?? article.category?.name ?? article.category_id ?? "-")}</p>
                <p>Status: ${escapeHTML(article.status)}</p>

                <hr><br>

                <p>${escapeHTML(article.content).replace(/\n/g, "<br>")}</p>

                <br>

                <label>Review Comment</label>
                <textarea id="reviewComment"
                    placeholder="Write a comment (optional)"></textarea>

                <button class="success" onclick="reviewAction(${id}, 'approve')">
                    Approve
                </button>

                <button class="danger" onclick="reviewAction(${id}, 'return')">
                    Return
                </button>

                <button class="secondary" onclick="showEditorDashboard()">
                    Back
                </button>
            </div>
        `;

    } catch (error) {
        showMessage(error.message);
    }
}

// APPROVE OR RETURN
async function reviewAction(id, action) {
    const comment = document.getElementById("reviewComment").value;

    const message = action === "approve"
        ? "Approve this article?"
        : "Return this article to author?";

    if (!confirm(message)) return;

    try {
        await api(`/editor/reviews/${id}/${action}`, "POST", {
            comment: comment
        });

        showMessage(
            action === "approve"
            ? "Article approved!"
            : "Article returned!"
        );

        showEditorDashboard();

    } catch (error) {
        showMessage(error.message);
    }
}

// ESCAPE HTML
function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

// HOME
document.getElementById("homeButton").addEventListener("click", () => {
    if (!currentUser) return;

    if (currentUser.role === "author") {
        showAuthorDashboard();
    } else {
        showEditorDashboard();
    }
});

// LOGOUT
function logout() {
    token = null;
    currentUser = null;

    localStorage.removeItem("token");

    dashboardPage.classList.add("hidden");
    loginPage.classList.remove("hidden");
}

document.getElementById("logoutButton").addEventListener("click", logout);

// AUTO LOGIN
if (token) {
    loadUser();
}
