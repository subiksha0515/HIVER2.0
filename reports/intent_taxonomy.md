# Customer Intent Taxonomy Report

## Taxonomy Overview
- **Total Intent Classes**: 11
- **Total Analyzed Conversations**: 81,480

## Intent Distribution Table
| Intent Name | Sample Count | Distribution % | Description |
|---|---|---|---|
| `SOFTWARE_UPDATE_ISSUES` | 1,326 | 1.63% | Inquiries regarding software updates, OS upgrade bugs, installation failures, or issues occurring immediately after updating. |
| `BATTERY_POWER_CHARGING` | 732 | 0.9% | Issues related to battery life, rapid battery draining, device turning off, or failing to charge. |
| `ACCOUNT_LOGIN_SECURITY` | 2,903 | 3.56% | Questions regarding account access, locked accounts, password reset, 2FA, or login authentication. |
| `APP_CRASH_PERFORMANCE` | 3,176 | 3.9% | Reports of application crashes, system lag, frozen screen, or apps failing to launch. |
| `BILLING_REFUND_SUBSCRIPTION` | 6,370 | 7.82% | Billing inquiries, unauthorized charges, refund requests, payment processing issues, or subscription cancellations. |
| `ORDER_SHIPPING_DELIVERY` | 23,778 | 29.18% | Questions about order status, shipment tracking, delayed delivery, or missing packages. |
| `CONNECTIVITY_NETWORK_WIFI` | 353 | 0.43% | Issues connecting to Wi-Fi, Bluetooth devices, cellular network data, or SIM card errors. |
| `AUDIO_SPEAKER_MICROPHONE` | 171 | 0.21% | Problems with sound output, low volume, distorted speaker sound, microphone unresponsiveness, or headphone connectivity. |
| `DISPLAY_SCREEN_PHYSICAL` | 614 | 0.75% | Issues involving physical screen damage, display flickering, black screen, or unresponsive touch input. |
| `STORE_REPAIR_SERVICE` | 2,985 | 3.66% | Requests for retail store appointments, hardware repair status, warranty service, or device replacement. |
| `OTHER / UNKNOWN` | 39,072 | 47.95% | Customer messages that do not confidently fit into any supported intent taxonomy category. |

## Detailed Intent Definitions & Inclusion/Exclusion Criteria

### Intent: `SOFTWARE_UPDATE_ISSUES`
- **Description**: Inquiries regarding software updates, OS upgrade bugs, installation failures, or issues occurring immediately after updating.
- **Inclusion Criteria**: Mentions software updates, OS version, update installation, or issues starting right after an update.
- **Exclusion Criteria**: Hardware physical damage, simple app store billing issues, or shipping queries.
- **Sample Count**: 1,326
- **Representative Customer Examples**:
  - *"@115850 Why can't the updates move properly https://t.co/DMwBAxwJUV"*
  - *"@117634 I love my new Kindle Oasis! Please tell me that immersion reading will be added in a future update?!"*
  - *"@AmazonHelp How do I disable notifications indicated by the bell icon in upper left corner of iOS Kindle app?"*
  - *"Hey @115850 @AmazonHelp I need an update on my refund! Can you help?"*
  - *"Hey @115821 wth does this mean? How can the iOS app on the phone be offline? #AmazonEcho https://t.co/bsAmAY4b38"*

### Intent: `BATTERY_POWER_CHARGING`
- **Description**: Issues related to battery life, rapid battery draining, device turning off, or failing to charge.
- **Inclusion Criteria**: Contains terms like battery, charging, power, battery drain, charger, cable.
- **Exclusion Criteria**: General software app crashes unless battery is explicitly cited.
- **Sample Count**: 732
- **Representative Customer Examples**:
  - *"@AmazonHelp where can I chat with a support member for a false charge"*
  - *"Haha @117634 has been sneakily charging me $9.99 SINCE FEBRUARY for a service I never use💩🙈👎 $90 gone!!! Thanks @AmazonHelp"*
  - *"@AmazonHelp when do you guys charge for the Xbox one X I preordered? It ships the 6th."*
  - *"@115850 : what type of product are you selling, we could have died.product was in use and then a blast Order no - 407-2808023-6902735 https://t.co/a8t07gJDuh"*
  - *"Amazon is starting to piss me off. All of the sudden it wants to charge me money to return shit. No thank you. @115821"*

### Intent: `ACCOUNT_LOGIN_SECURITY`
- **Description**: Questions regarding account access, locked accounts, password reset, 2FA, or login authentication.
- **Inclusion Criteria**: Mentions login, password, locked account, credentials, or account verification.
- **Exclusion Criteria**: Billing disputes without account access issues.
- **Sample Count**: 2,903
- **Representative Customer Examples**:
  - *"@115823 I want my amazon payments account CLOSED. dm me please."*
  - *"Bought an @115821 Echo Show and it won’t recognize a single @AmazonHelp account in our household. WTF, guys?"*
  - *"@AmazonHelp if I add another adult to my Amazon household (with their own account) can they see my wishlists/photos/order history?"*
  - *"@AmazonHelp i reset my password 3 times and it still says incorrect you gotta be shitting me"*
  - *"@AmazonHelp um, my account was locked as soon as I tried to login on desktop. I still haven’t received an email on how to get it unlocked..."*

### Intent: `APP_CRASH_PERFORMANCE`
- **Description**: Reports of application crashes, system lag, frozen screen, or apps failing to launch.
- **Inclusion Criteria**: Mentions app freezing, crashing, unresponsive UI, or slow performance.
- **Exclusion Criteria**: Physical screen damage or internet network connectivity issues.
- **Sample Count**: 3,176
- **Representative Customer Examples**:
  - *"@115821 please spend time &amp; money to fix your app. Constant issues with it."*
  - *"My Kindle not working properly is breaking my heart! 😩💔"*
  - *"@AmazonHelp Trying to get a friend's playlist on my Amazon music app but it keeps giving me the following message https://t.co/o6zINm6HBC"*
  - *"@117093 Hey yall. Why is my checkout not working? I click "checkout with fresh" and it takes me to an error page. What's the deal?"*
  - *"Seriously @115821 what is up with ordering things and it being open? You guys shipping returned items. 2nd day in a row this happens :SMH: https://t.co/gMyT1z9Zu1"*

### Intent: `BILLING_REFUND_SUBSCRIPTION`
- **Description**: Billing inquiries, unauthorized charges, refund requests, payment processing issues, or subscription cancellations.
- **Inclusion Criteria**: Contains billing terms, payment, charge, refund, money, receipt, or subscription.
- **Exclusion Criteria**: Physical store hardware returns.
- **Sample Count**: 6,370
- **Representative Customer Examples**:
  - *"@AmazonHelp I called customer service and was told my membership wouldn't be renewed. I was just charged today. How do I get a refund? https://t.co/SeoQUsA0VA"*
  - *"@115821 being charged for amazon prime &amp; when I go to cancel it, it’s saying I’m not a member😠😠😠"*
  - *"@115830 amazonuk took money without any https://t.co/w25zXi7DYp they are not giving it back nor giving clear statement of my refund proces"*
  - *"@115830 you pay for prime expecting next day delivery. Then receive 2 emails half hr apart 'failed delivery' but your sitting at home 😡"*
  - *"@115821 why do I pay for 2 day shipping and it's going on 4 days."*

### Intent: `ORDER_SHIPPING_DELIVERY`
- **Description**: Questions about order status, shipment tracking, delayed delivery, or missing packages.
- **Inclusion Criteria**: Mentions order number, shipping, tracking, delivery status, or package delivery.
- **Exclusion Criteria**: Digital app store downloads.
- **Sample Count**: 23,778
- **Representative Customer Examples**:
  - *"@115830 my package was ‘accidentally’ opened.. 4 items missing worth £97. You need better delivery drivers!! https://t.co/f6SaVBSMqM"*
  - *"@115821 @AmazonHelp why is my order at my local courier for the last 6 days and still hasn’t been delivered to me?? Over 1 week late 😡"*
  - *".@AmazonHelp Item has not been delivered but tracking says it was handed to me over an hour ago... 2nd time this has happened. Sort it out https://t.co/42W82GcARk"*
  - *"@AmazonHelp delivery I paid for today,didn’t arrive.why not?i paid enough for it.where is it??I’m unhappy.refund the delivery charge"*
  - *"Anna Inspired in idea lab at school to be @115821 package being shipped to Narnia! "Amazon can go anywhere" according to Anna. https://t.co/TyvKhuu7su"*

### Intent: `CONNECTIVITY_NETWORK_WIFI`
- **Description**: Issues connecting to Wi-Fi, Bluetooth devices, cellular network data, or SIM card errors.
- **Inclusion Criteria**: Mentions Wi-Fi, Bluetooth, network connection, SIM, cellular data, or pairing.
- **Exclusion Criteria**: Power/battery issues.
- **Sample Count**: 353
- **Representative Customer Examples**:
  - *"I lost my signal while searching something in @115821 and since the page didn't load, this shows up...I am not even mad. #DogsForLife https://t.co/QhdOmksrrY"*
  - *"@115850 : can we connect echo dot to videocon smart tv? If yes, how?"*
  - *"Hey @115821: the 4K FireTV is great, but not needing to restart after every sleep to have it find my WiFi network would be better."*
  - *"@AmazonHelp why is Videos option missing in the skills for Alexa in India? Not able to connect my fire TV."*
  - *"Tem coisa melhor do q receber encomenda no teu nome e ainda antes da data prevista?? @117086 te amo, namoral https://t.co/ydD9ZNF0U4"*

### Intent: `AUDIO_SPEAKER_MICROPHONE`
- **Description**: Problems with sound output, low volume, distorted speaker sound, microphone unresponsiveness, or headphone connectivity.
- **Inclusion Criteria**: Mentions sound, volume, speaker, mic, audio, or headphones/AirPods.
- **Exclusion Criteria**: Display screen issues.
- **Sample Count**: 171
- **Representative Customer Examples**:
  - *"I have 2 echos and set up multi room music playback. How do you switch back and forth between multi room audio and playing on only one? Sometimes I like whole house, sometimes I don't want to wake up my wife. @115833 #echo #alexa"*
  - *"@117795 Now that I’m streaming to your Prime Do U have audio assisted movies, TV, etc. as I am visually impaired. ?"*
  - *"@115830 I don’t think I ordered this with my headphone jack.. 🤢🤢 https://t.co/aJbEVjQO3y"*
  - *"@5503 I’m enjoying the @128020 Experience on the @115833 dot. However, I’d prefer to stream it through @118117 speaker. Alexa can’t manage that, despite repeated attempts. During the most recent attempt, Alexa thought I wanted, um, this: https://t.co/VsWvhMHake"*
  - *"@AmazonHelp just received the munchkin nursery projector and sound system and the volume does not work."*

### Intent: `DISPLAY_SCREEN_PHYSICAL`
- **Description**: Issues involving physical screen damage, display flickering, black screen, or unresponsive touch input.
- **Inclusion Criteria**: Contains terms like screen, display, flicker, black screen, touchscreen.
- **Exclusion Criteria**: Software update bugs with display working fine.
- **Sample Count**: 614
- **Representative Customer Examples**:
  - *"@115850 I have ordered one black and grey backpack of Polestar and I received complete pink backpack which I never ordered"*
  - *"@115850 : Got a really bad experience with support for replacing cracked Kult Mobile. You ask to contact Kult and they point you. https://t.co/Krh5BolYua"*
  - *"@115850 @115851 @1840 pathetic service for Amazon business, bihmsen service representative can't even put me touch with manager."*
  - *"Anyone know how you mirror on the new Amazon Fire TV? @116439 want to screen mirror #amazonfiretv #fireTV"*
  - *"Si je dois faire un achat pour le Black Friday, ça sera la montre Samsung Gear S3. Je compte sur vous @120533"*

### Intent: `STORE_REPAIR_SERVICE`
- **Description**: Requests for retail store appointments, hardware repair status, warranty service, or device replacement.
- **Inclusion Criteria**: Mentions store appointment, repair, service center, warranty, or hardware replacement.
- **Exclusion Criteria**: Self-service software troubleshooting.
- **Sample Count**: 2,985
- **Representative Customer Examples**:
  - *"Way to drop the ball on customer service @115821 so pissed right now!"*
  - *"@116090 I signed up for Prime so I could preorder Battlefront II and get all the bonuses and now cust service is saying I won’t get bonus"*
  - *"@116935 worst customer service; got hung up on twice"*
  - *"#Halloween #goldenretriever #dogs #puppy @115821 6 month old service dog Halloween https://t.co/WOoQOFCXiM"*
  - *"Changed your mind about something you bought? Have no fear. Replace products with ease on Amazon. https://t.co/mESIpKkCpK"*

### Intent: `OTHER / UNKNOWN`
- **Description**: Customer messages that do not confidently fit into any supported intent taxonomy category.
- **Inclusion Criteria**: Messages with low confidence, general greetings, ambiguous text, or off-topic queries.
- **Exclusion Criteria**: Messages clearly matching a defined domain intent.
- **Sample Count**: 39,072
- **Representative Customer Examples**:
  - *"@115825 also, beim Addams Family-Film in Prime sind Bild und Ton nicht wirklich synchron. Wie kommt's?"*
  - *"PLAYERUNKNOWN'S BATTLEGROUNDS is now available for preorder on Xbox One consoles - https://t.co/bqLHcBDqAb https://t.co/muLIqeHq0o"*
  - *"Thanks for the style advice, @115833 look ...I think? #Halloween2017 #flamingo https://t.co/XvI54La043"*
  - *"In response to your @115830 packing video, this packaging was for a 2ft washing line pole @115837 https://t.co/X21SQHgC0K"*
  - *"@AmazonHelp Is it possible to prevent AMZL from delivering my packages moving forward? Stuff is either lost/stolen/broken EVERY time."*
