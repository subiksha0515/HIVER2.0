# Historical Support-Response Retrieval Evaluation Report

## Executive Summary
This report evaluates the dense semantic vector retrieval system on **5,000 held-out test conversations**.
The retrieval index was constructed strictly on training data (`train.jsonl`) to guarantee **zero train/test data leakage**.

## Retrieval Quantitative Evaluation Metrics
| Metric | Score | Description |
|---|---|---|
| **Recall@1** | **0.6484** | Fraction of test queries where Top-1 retrieved historical case matches true intent |
| **Recall@3** | **0.8558** | Fraction of test queries where at least one of Top-3 cases matches true intent |
| **Recall@5** | **0.9002** | Fraction of test queries where at least one of Top-5 cases matches true intent |
| **MRR (Mean Reciprocal Rank)** | **0.7460** | Average reciprocal rank of the first intent-matching historical case |

## Representative Successful Retrieval Examples
### Successful Case 1 (`conv_668464`)
- **Test Query Customer Message**: *"きた＼(^^)／昨日の夜中に頼んでもう届くAmazonて本当に優秀＼(^^)／充電して明日持ってこ＼(^^)／しかし本当にこの顔可愛いな~~！！ https://t.co/66gyQ8hktT"*
- **Query Intent**: `OTHER / UNKNOWN`
- **Top-1 Retrieved Customer Message**: *"朝いきなりAmazon有料サイトてきたあ(＞＜)こわっいいいい https://t.co/EtCZ6oi0fU"*
- **Top-1 Retrieved Brand Response**: *"@320165 失礼します。こちらは当サイトからお送りしたものではございません。AmazonからSMSで未納料金などといったメールは送信いたしません。 ヘルプページでも注意喚起を行っておりますので、ご参照ください。https://t.co/k4jy2iTq1Y RI"*
- **Top-1 Similarity Score**: `1.0000`
- **Top-1 Retrieved Intent**: `OTHER / UNKNOWN`

### Successful Case 2 (`conv_475067`)
- **Test Query Customer Message**: *"I'll say this for @115830 - their customer service is utterly top notch. I've never been left frustrated by dealing with them and they always resolve issues quickly. Lots of companies could learn a lot from them."*
- **Query Intent**: `STORE_REPAIR_SERVICE`
- **Top-1 Retrieved Customer Message**: *"@115821 customer service is just amazing. I’ve been impressed by them multiple times and never had a bad experience. 👍"*
- **Top-1 Retrieved Brand Response**: *"@214236 Thanks for taking the time to share this! 💓We all hope you enjoy the rest of the day! ^EP"*
- **Top-1 Similarity Score**: `0.5781`
- **Top-1 Retrieved Intent**: `STORE_REPAIR_SERVICE`

### Successful Case 3 (`conv_2575249`)
- **Test Query Customer Message**: *"So, if my packages that I ALREADY reordered don't get here by 8pm, I expect next day shipping for free. I need these items no later than Saturday and y'all playing @115821 @118706 @AmazonHelp"*
- **Query Intent**: `ORDER_SHIPPING_DELIVERY`
- **Top-1 Retrieved Customer Message**: *"@115821 y'all owe me 6 bucks for missing that "next day shipping""*
- **Top-1 Retrieved Brand Response**: *"@334211 I'm sorry to hear this, Harrison! Just to confirm, did we miss the date provided in your order confirmation email? ^HC"*
- **Top-1 Similarity Score**: `0.5959`
- **Top-1 Retrieved Intent**: `ORDER_SHIPPING_DELIVERY`

### Successful Case 4 (`conv_80563`)
- **Test Query Customer Message**: *"@AmazonHelp your cust Serv staff are continuing to jerk me around.... and are not helpful at all with me getting my packages on time."*
- **Query Intent**: `OTHER / UNKNOWN`
- **Top-1 Retrieved Customer Message**: *"Time to cancel @115821 prime until ur couriers can actually get me my packages on time, or at all.Nothing but problems with AZL. @AmazonHelp"*
- **Top-1 Retrieved Brand Response**: *"@477422 I'm sorry for the poor experience! Please provide more information here: https://t.co/WV75PdaSLE so we can take a closer look ^TN"*
- **Top-1 Similarity Score**: `0.5891`
- **Top-1 Retrieved Intent**: `OTHER / UNKNOWN`

### Successful Case 5 (`conv_1665832`)
- **Test Query Customer Message**: *"@AmazonHelp can you explain this? It was supposed to be delivered today and I got no call.it was a gift and I was relying on you guys https://t.co/j1YF9yuJuy"*
- **Query Intent**: `ORDER_SHIPPING_DELIVERY`
- **Top-1 Retrieved Customer Message**: *"@115821 my stuff was supposed to be delivered by 8:00 pm today. It's 8:01. https://t.co/6tqRapjOZy"*
- **Top-1 Retrieved Brand Response**: *"@374618 I'm sorry you haven't received your order. What's the current tracking status and carrier? See: https://t.co/q4LAMZ3tbE ^AM"*
- **Top-1 Similarity Score**: `0.6420`
- **Top-1 Retrieved Intent**: `ORDER_SHIPPING_DELIVERY`

## Representative Failed Retrieval Examples & Failure Mode Analysis
### Failed Case 1 (`conv_2640926`)
- **Test Query Customer Message**: *"ONCE AGAIN, Y'ALL PLAYING @123967 @AmazonHelp BECAUSE I KNOW MY PACKAGE WILL NOT BE HERE BY 8PM. THE POST MAN CAME AND WENT: TRACKING HASN'T BEEN UPDATED SINCE YESTERDAY AT 2:47 PM. I'M TIRED. https://t.co/2pNGmZ9n7A"*
- **Query Intent**: `ORDER_SHIPPING_DELIVERY`
- **Top-1 Retrieved Customer Message**: *"@AmazonHelp Anyone to roughly know when my parcel will be with me today? The tracking id hasn't been updated since yesterday"*
- **Top-1 Retrieved Brand Response**: *"@522980 Hey Ben. We don't have access to account info here. Please reach out - https://t.co/JzP7hlA23B we'll be happy to help. ^TP"*
- **Top-1 Similarity Score**: `0.5052`
- **Top-1 Retrieved Intent**: `SOFTWARE_UPDATE_ISSUES`

### Failed Case 2 (`conv_2976490`)
- **Test Query Customer Message**: *"@AmazonHelp 3rd order that has been “lost” when being delivered using your delivery service. Chat and phone support was useless."*
- **Query Intent**: `ORDER_SHIPPING_DELIVERY`
- **Top-1 Retrieved Customer Message**: *"@AmazonHelp Your phone support is horrendous. Total garbage"*
- **Top-1 Retrieved Brand Response**: *"@511109 Hi, sorry to hear that you had a bad experience. Can you tell us more without sharing any personal or acc info? ^JJ"*
- **Top-1 Similarity Score**: `0.4929`
- **Top-1 Retrieved Intent**: `OTHER / UNKNOWN`

### Failed Case 3 (`conv_422505`)
- **Test Query Customer Message**: *"Amazonプライム会員解約してなくて年会費取られてる_(:3」∠)_ はああああああああああああ"*
- **Query Intent**: `OTHER / UNKNOWN`
- **Top-1 Retrieved Customer Message**: *"Can y’all stop telling me things are Prime Eligible if y’all aren’t gonna deliver my stuff in 2 days 🙃🙃🙃 @AmazonHelp"*
- **Top-1 Retrieved Brand Response**: *"@186341 We don't want to let you down! Have we missed our expected delivery date? Check here: https://t.co/Y5jpI9gRhE ^JE"*
- **Top-1 Similarity Score**: `0.0000`
- **Top-1 Retrieved Intent**: `ORDER_SHIPPING_DELIVERY`

### Failed Case 4 (`conv_339930`)
- **Test Query Customer Message**: *"@115821 Hey, just a thought. Packing a 28lb bag of cat litter &amp; a 15lb bag of cat food in the same box. Not a good idea. Poor ups man’s back"*
- **Query Intent**: `OTHER / UNKNOWN`
- **Top-1 Retrieved Customer Message**: *"Hey @AmazonHelp, you probably shouldn't ship printer cartridges in the same box with an Instapot https://t.co/rhQ6H9jF6G"*
- **Top-1 Retrieved Brand Response**: *"@260136 I'm sorry for the condition of your items. Have you explored return options here: https://t.co/MGSiLyzBrm? Packaging feedback can be left separately. Learn how here: https://t.co/JjiPwdDV3Z ^JF"*
- **Top-1 Similarity Score**: `0.5486`
- **Top-1 Retrieved Intent**: `ORDER_SHIPPING_DELIVERY`

### Failed Case 5 (`conv_2400623`)
- **Test Query Customer Message**: *"@120474 Where should I have listed the name of tickets I bought as a gift during purchase? I had no option when buying."*
- **Query Intent**: `BILLING_REFUND_SUBSCRIPTION`
- **Top-1 Retrieved Customer Message**: *"@115850 I deleted my tweet as requested by you, Where should I raised my concern ?"*
- **Top-1 Retrieved Brand Response**: *"@169508 Please click here: https://t.co/GIJyeYqKE0. So that we can check and look into it. ^SB"*
- **Top-1 Similarity Score**: `0.4248`
- **Top-1 Retrieved Intent**: `OTHER / UNKNOWN`

## Key Retrieval Failure Modes
1. **Short Ambiguous Messages**: Customer queries containing only single-word complaints (e.g. *"Help @AmazonHelp"*) lack topic tokens, causing retrieval to pull arbitrary generic support queries.
2. **Multiple Overlapping Intents**: Queries containing both shipping delays and billing charges (e.g. *"I was charged for 2-day delivery but it arrived 4 days late"*) match both `ORDER_SHIPPING_DELIVERY` and `BILLING_REFUND_SUBSCRIPTION` centroids.
3. **Non-Standard Twitter Jargon & Emojis**: Queries composed primarily of URLs, handles, or emojis reduce semantic match precision.

## Reproducibility Commands
```bash
python -m src.retrieval.index
python -m src.retrieval.evaluate
```