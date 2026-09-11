# Dataset Analysis Report - Kaggle Twitter Customer Support

## 1. Overview Statistics
- **Total Rows**: 2,811,774
- **Total Columns**: 7
- **Date Range**: 2008-05-08 20:13:59+00:00 to 2017-12-03 23:14:01+00:00
- **Customer Tweets (Inbound)**: 1,537,843 (54.69%)
- **Brand Tweets (Outbound)**: 1,273,931 (45.31%)
- **Unique Authors**: 702,777
- **Unique Brands**: 106

## 2. Column Specifications & Missing Values
| Column Name | Data Type | Missing Count | Missing % |
|---|---|---|---|
| `tweet_id` | `str` | 0 | 0.0% |
| `author_id` | `str` | 0 | 0.0% |
| `inbound` | `bool` | 0 | 0.0% |
| `created_at` | `str` | 0 | 0.0% |
| `text` | `str` | 0 | 0.0% |
| `response_tweet_id` | `str` | 1,040,629 | 37.01% |
| `in_response_to_tweet_id` | `str` | 794,335 | 28.25% |

## 3. Data Quality Assessment
- **Exact Duplicate Rows**: 0
- **Duplicate Tweet IDs**: 0
- **Tweets with `in_response_to_tweet_id`**: 2,017,439
- **Tweets with `response_tweet_id`**: 1,771,145
- **Extremely Short Messages (< 10 chars)**: 1,295
- **Long Messages (> 280 chars)**: 22,618
- **Mean Text Length**: 113.89 characters (Median: 115.0)

## 4. Top 15 Brands by Volume
| Rank | Brand handle (`author_id`) | Total Brand Tweets |
|---|---|---|
| 1 | `AmazonHelp` | 169,840 |
| 2 | `AppleSupport` | 106,860 |
| 3 | `Uber_Support` | 56,270 |
| 4 | `SpotifyCares` | 43,265 |
| 5 | `Delta` | 42,253 |
| 6 | `Tesco` | 38,573 |
| 7 | `AmericanAir` | 36,764 |
| 8 | `TMobileHelp` | 34,317 |
| 9 | `comcastcares` | 33,031 |
| 10 | `British_Airways` | 29,361 |
| 11 | `SouthwestAir` | 28,977 |
| 12 | `VirginTrains` | 27,817 |
| 13 | `Ask_Spectrum` | 25,860 |
| 14 | `XboxSupport` | 24,557 |
| 15 | `sprintcare` | 22,381 |

## 5. Key Quality Insights & Pipeline Decisions
1. **Preservation of Customer Natural Language**: No aggressive text stemming or stopword removal will be performed on raw tweets to preserve semantic intent and tone.
2. **Missing In-Reply Links**: A subset of inbound tweets lack `in_response_to_tweet_id` (starting new threads), while outbound brand tweets heavily use `in_response_to_tweet_id` linking back to customer queries.
3. **Multi-Response Complications**: Some brand replies link multiple response tweet IDs separated by commas. Graph reconstruction handles comma-separated lists to reconstruct complete conversation trees.
