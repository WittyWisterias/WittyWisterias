<h1 align="center">
    💩 ShitChat: The best worst Chat you've ever used
</h1>

**Witty Wisterias** Python Discord Summer CodeJam 2025 project.
The technology is **Python in the Browser**, the theme is **Wrong Tool for the Job**, and our chosen framework
is [Reflex](https://github.com/reflex-dev/reflex).

---

Are you searching for a 100% private, secure, end2end-encrypted chat application, hosted for free publicly?
<br/>
And do you want it to be hosted in Images on a Free Image Hoster, with the Chat Inputs beeing to wrong way arround?
<br/>
Then look no further, because **ShitChat** is the ~~wrong~~ right tool for you!


## Naming
Wondered where the name **ShitChat** comes from?
The name is a play on words, coming from [`Chit Chat`](https://dictionary.cambridge.org/dictionary/english/chit-chat) and Shit, as the Chat App is quite shitty...

## Getting Started

1. Clone the repository:
   ```shell
   git clone https://github.com/WittyWisterias/WittyWisterias/
   cd WittyWisterias
   ```
2. Install the dependencies:
   ```shell
   pip install -r requirements.txt
   ```
3. Start a local Reflex Server:
   ```shell
   cd witty_wisterias
   reflex run
   ```
4. Allow Python access to your Webcam if prompted.
5. Open your browser and navigate to http://localhost:3000.
6. Chat!

## Video Presentation

https://github.com/user-attachments/assets/34d2b84e-76cb-40d1-8aca-c71dcacdc9dd

(Unmute for some grooves)


## Wrong Tool for the Job
<details>
    <summary>Theme Aspects ✅</summary>

- Having to hold Handwritten Messages in front of your Webcam to send Text Messages
- Having to describe your image to send Image Messages
- Hosting the complete Chat Database in one Image File on an Free Image Hoster

Note: We searched for wrong tools for the Cryptography, with one of more promising candidates being regex based
encryption, but we decided to not sacrifice user security and privacy for the sake of the theme.

</details>

## Features
<details>
    <summary>Features Summary 💡</summary>

- Free and Open Database hosted as Image Files on [freeimghost.net](https://freeimghost.net/search/images/?q=ShitChat)
- 100% Private and Secure, no Backend Server needed
- Full Chat History stored in the Image Stack
- Creation of a Unique UserID, Sign-Verify / Public-Private Key Pair on first Enter
- Automatic Sharing of Verify and Public Keys in the Image Stack
- Signed Messages in Public Chat to protect against impersonifications
- End2End Encryption of Private Messages
- Storage of own Private Messages in Local Storage, as they cannot be self-decrypted
- Storage of others Verify / Public Keys in LocalStorage to protect against Image Stack/Chat History Swap Attacks
- Customization of your User Name and Profile Picture
- Sending Text via Webcam OCR using [olmocr.allenai.org](https://olmocr.allenai.org/)
- Sending Images via Image Generation using [pollinations.ai](https://pollinations.ai/)

</details>

## Privacy and Security
<details>
    <summary>Information about your Privacy 🔐</summary>

- **No guarantee of Privacy or Security**: Even though **ShitChat** uses common, SOTA compliant cryptographic algorithms, the Chat app has not been audited for security. Use at your own risk.
- **No End2End Encryption of Public Messages**: Public Messages are, as the name says, public. They however are signed to protect against impersonification.
- **No guarantee of UserInput Privacy**: We use [olmocr.allenai.org](https://olmocr.allenai.org/) for OCR and [pollinations.ai](https://pollinations.ai/) for Image Generation. Only the results of these APIs will be shared in the Chat (so your webcam image will not be shared in the Chat). We cannot guarantee the Privacy of your Data shared with these APIs, however they do have strict Privacy Policies.
- **Use UserID to verify Identities**: The UserID is your only way to verify the identity of a user. Username and Profile Image can be changed at any time, and duplicated by another user.
- **Reliant on Local Storage**: **ShitChat** is only secure against "Database Swap" attacks as long as you do not clear your browser's local storage or switch browsers. If you do so, you will be at the risk of an Image Stack/Chat History Swap Attack.
- **Open to Everyone**: There is no friend feature, you can be Private Messaged by anyone.

</details>


## Preview Images
<details>
    <summary>Preview Images 📸</summary>

### See the latest Encoded ChatApp Message Stack:
https://freeimghost.net/search/images/?q=ShitChat

#### Public Chat:
<img width="1000" alt="Public Chat" src="https://github.com/user-attachments/assets/cedf19bc-6e5d-48df-b6da-a66f3c9cf202" />

#### Private Chat:
<img width="1000" alt="Private Chat" src="https://github.com/user-attachments/assets/f3d09c98-4bc4-4ced-a216-30d26c48dfaa" />

#### Text Message Form:
<img width="500" alt="Text Message Form" src="https://github.com/user-attachments/assets/046b4da1-aeb9-4d6d-b0ad-8f95b970a180" />


#### Image Message Form:
<img width="500" alt="Image Message Form" src="https://github.com/user-attachments/assets/2fa4c74f-65eb-4c74-9995-ccbf6ee4b0f8" />


</details>

# Credits
This project was created by (in order of contributed LOC):

| [Vinyzu](https://github.com/Vinyzu)                                                                           | [erri4](https://github.com/erri4)                                                                         | [Ben Gilbert](https://github.com/bensgilbert)                                                                                     | [Pedro Alves](https://github.com/pedro-alvesjr)                                                                                       | [Tails5000](https://github.com/Tails5000)                                                                                 |
|---------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| [<img src="https://github.com/vinyzu.png" alt="vinyzu" title="Vinyzu" width="66">](https://github.com/vinyzu) | [<img src="https://github.com/erri4.png" alt="erri4" title="erri4" width="66">](https://github.com/erri4) | [<img src="https://github.com/bensgilbert.png" alt="bensgilbert" title="Ben Gilbert" width="66">](https://github.com/bensgilbert) | [<img src="https://github.com/pedro-alvesjr.png" alt="pedro-alvesjr" title="Pedro Alves" width="66">](https://github.com/pedro-alvesjr) | [<img src="https://github.com/Tails5000.png" alt="Tails5000" title="Tails5000" width="66">](https://github.com/Tails5000) |
| Chat App                                                                                                      | Database, Backend                                                                                         | First Frontend                                                                                                                    | Message Format                                                                                                                        | OCR Research                                                                                                              |
