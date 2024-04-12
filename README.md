# Welcome to Linkifyer!<!-- omit in toc -->

Linkifyer is your personalized link organizer designed to simplify your web browsing experience. Whether you're bookmarking articles, saving videos, or organizing NSFW content, Linkifyer is here to help you keep everything neat and secure.

- [Disclaimer](#disclaimer)
- [Installation and Usage](#installation-and-usage)
- [How to Use Linkifyer](#how-to-use-linkifyer)
- [Security and Privacy](#security-and-privacy)
- [Technical Details](#technical-details)
- [Routes](#routes)
- [Join the Linkifyer Community](#join-the-linkifyer-community)
- [License](#license)

Before using the Linkifyer application, please read the following disclaimer:

## Disclaimer

By running the Linkifyer application, you agree to assume sole responsibility for its usage and any consequences thereof. The developers of Linkifyer do not endorse or encourage any specific use of the application, including but not limited to the storage or organization of NSFW content. Users are expected to abide by all applicable laws and regulations while using Linkifyer and must ensure that their usage complies with their local jurisdiction's policies and guidelines.

## Installation and Usage

Getting started with Linkifyer is a breeze! Simply double-click `linkifyer.exe` to launch the application, or go to [http://localhost:9191](http://localhost:9191) in your web browser to access the local server.

## How to Use Linkifyer

1. **Register with a Username and Password**: Start by registering for an account on Linkifyer. Simply choose a username and password to create your account. This registration occurs locally on your computer, ensuring your data stays secure and private.

2. **Login**: After registering, log in to your Linkifyer account using your chosen username and password. This will grant you access to all the features of the app.

3. **Browse the Web for Your Favorite Link**: Once logged in, browse the web using your preferred browser to find the link you want to save. It could be an interesting article, a helpful video, or any other online resource you wish to keep track of.

4. **Paste the Link into the "Get Link" Section on Home and Click Get**: After finding the desired link, copy it from your browser's address bar. Then, navigate to the "Home" section of the Linkifyer app and paste the link into the designated "Get Link" section. Click on the "Get" button to proceed.

5. **Adjust Title, Tags and Description on the Search Page**: Upon clicking "Get," Linkifyer will redirect you to the search page. Here, you can adjust the title, add tags and a description to categorize your saved link.

6. **Click "Save"**: Once you've customized the title and tags, click on the "Save" button to store the link in your Linkifyer Library.

7. **Access Your Library**: After saving the link, Linkifyer will automatically redirect you to your Library. Here, you can see and filter all your saved links, making it easy to find what you're looking for.

8. **Secure Logout**: Whenever you're finished viewing your links or want to secure your account, simply log out securely. This ensures that only you can access your saved content in Linkifyer.

## Security and Privacy

At Linkifyer, we take your security and privacy seriously. All your data is stored locally on your computer, and we never download media – only thumbnails for easy identification. We don't share your information with anyone, and you're responsible for how you use the app.

## Technical Details

You can pass command-line arguments to the executable for specific behaviors:

- `dev`: Run Linkifyer in development mode with debugging enabled.
- `incognito`: Opens the application in an incognito window in Google Chrome.
- `https`: Enable HTTPS protocol for secure connections (not tested).
- `host`: Specify the host address. Default is localhost.
- `port`: Set the port number for the server. Default is 9191.
- `prefix`: Define a custom site prefix (mainly for reverse proxy). Default is /.

```shell
# in commandline run
linkifyer.exe --dev --port 9090 --incognito --prefix /myprefix

# --dev (debugging mode enabled)
# --port 9090 (launches app in port 9090, http://localhost:9090)
# --incognito (launches chrome in incognito mode)
# --prefix /myprefix (custom site prefix added, http://localhost:9090/myprefix)
```

## Routes

- `/`: Home page.
- `/about`: About page.
- `/library`: Library page for managing items.
- `/search`: Search page for searching items.
- `/save`: Endpoint for submitting item data.
- `/delete/<user_id>/<item_hash>`: Endpoint for deleting an item.
- `/register`: Registration page for new users.
- `/login`: Login page for existing users.
- `/logout`: Logout endpoint.

## Join the Linkifyer Community

Join thousands of users who trust Linkifyer to organize their online content securely and efficiently. Start exploring the web with confidence, knowing that Linkifyer has your back every step of the way.



## License

Linkifyer is licensed under the MIT License.



___

*Note: Linkifyer is powered by Python and Flask. For technical documentation and code details, refer to the provided source files.*

