# Eliteworks website - setup guide

## 1. The one file to edit: `js/config.js`
Company name, logo, phone, email, address, social links, Web3Forms key, testimonials key, GitHub details,
gallery photos and association logos are all in `js/config.js`. Change it once and every page updates.

After editing, run `python3 _source/build.py` (needs Python 3). This refreshes page titles, SEO tags,
canonical links and the sitemap. If you cannot run Python, the visible changes (name, logo, phone, email,
WhatsApp, address, social links, form key) still update on every page automatically from `config.js`.
Only the search-engine text in the HTML keeps the old name until you rebuild.

## 2. Contact and careers forms (Web3Forms)
1. Go to https://web3forms.com and enter your email to get a free Access Key.
2. Paste it into `web3formsKey` in `js/config.js`.

## 3. Host on GitHub Pages
1. Create a GitHub repository (for example `eliteworks`) and upload all files in this folder.
2. Put your GitHub username in `githubUser` and the repository name in `repo` (config.js), then run the build.
3. Repository -> Settings -> Pages -> Source: "Deploy from a branch" -> Branch: `main`, folder `/ (root)`.
4. Your site will be at `https://USERNAME.github.io/REPO/`. For your own domain, set `customDomain` in config.js
   and add the domain in the Pages settings.

## 4. Customer testimonials (Google Sheet, free)
Customers submit a review on the Testimonials page. It lands in your Google Sheet and you tick one box to publish it.
1. Create a new blank Google Sheet. Menu: Extensions -> Apps Script.
2. Delete the existing code, paste all of `_source/testimonials-apps-script.gs`, press Save.
3. Choose the function `doGet` in the toolbar and press Run. Allow the permissions
   (Advanced -> Go to project (unsafe) -> Allow). This is your own script.
4. Deploy -> New deployment -> type "Web app". Execute as: Me. Who has access: Anyone. Deploy.
5. Copy the Web app URL and paste it into `testimonialsApi` in `js/config.js`.
6. Open the Sheet, tab "Testimonials". Tick the "Approved" box on a row to show it on the website; untick to hide it.

Set `AUTO_APPROVE = true` in the script (then Deploy -> Manage deployments -> Edit -> New version) if you want reviews to appear immediately without approval.

## 5. Photos and partners
- Gallery: put images in an `img/` folder and list them in `gallery` in config.js.
- Associations: list partner names/logos in `associations` in config.js.
