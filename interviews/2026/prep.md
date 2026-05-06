## NCM Strory

**Tell me about a time you owned a critical data system. Walk me through it.**

> I would like to talk about the New Consumption Metrics initiative which I’m currently owning at New Relic. It is a revenue forcasting model for the consumption across clients for New Relic and is consumed by the finance, product analytics and sales stakeholders including the CXOs. Basically NCM is a monthly revenue forcasting based on actual consumed MTD quantities and forecasting for the remaining of the month using rolling 28 day averages to get thru the estimated quantities being consumed by the client for the entire month for all the unit of measures and walking these quantities through a pricing mechanism to get the dollar value for all types of tiered/flat/ and various other buying programs. 

> The initiative involves using mediallian architechture to build raw, intermediate, mart, and reporting layers for the NCM metric. This is uses dbt, snowflake as core tech stack with airflow being used for orchestration. The project involves several analytical models like contract-to-date, period-to-date, savings plan depletion being developed for the use of stakeholders apart from the main NCM data model. 

> All in all the pipeline contains more than 250 models and 1450 test cases and accounts for almost 85M$ of monthly revenue across 18000 clients. Also the deligently pipeline handles cases like manual adjustments and overrides for any sort of human adjustments as and when needed.


**That's impressive scale. You mentioned 1450 test cases — walk me through your testing strategy. How did you decide what to test and how do you know the pipeline is actually trustworthy?**

> Yes, the testing actually involves a shift-left testing approach, which invloves the tests being run during model execution as well a peculiar case where a few tests run almost all the time for every 15 mins. 

> Let me wlak you thru the tests being run at the time of model execution first. I implemented both dbt native tests and custom tests developed to support business logic. Whn it comes to the bronze layer most of the tests include like freshness, not-null and type-casting tests for the readiness in the data quality. When it comes to silver layer, it is the place where most diverse tests lie, like dbt built-in unique combination of columns, accepted values, expresion_is_true to expect_row_values_to_have_date_for_every_n_datepart and so on. Coming to the business tests which reads like the churned account must exist till the end of month, monthly forecast should always be greater than or equal to MTD values etc exist at the flag-end of the pipeline mostly. Also we recently added z-score based anamoly tests executed via a macro to find outliers in the numerical metric columns for a few models. As a variety of tests are being covered at silver layer, the golden layer as it is mostly 1:1 views covers lesser tests confined to basics like unique combination of column and not nulls if there involves joins in them. 

> These are tests are configured to either warn or throw errror in the pipeline to stop it depending on the severity of the test.


**Proration Bug**

> I caught it manually during a data inspection pass — the tests didn't flag it because the numbers were internally consistent, just wrong for a specific edge case. What tipped me off was seeing constant quantities persisting for several days on certain accounts post-migration, which shouldn't happen in a consumption model. Given this feeds $85M in monthly revenue and sales incentives, I treated it as high priority immediately. It took a few days to trace because it was buried mid-pipeline — the proration comparison was happening at the wrong grain. Once I understood the migration reset behaviour, the fix was to compare against prorated minimum commits rather than the full commit value. The tricky part was understanding the business logic well enough to know what the correct number should be — not just making the test pass.


**Tell me about a time you had to push back on a stakeholder or influence a decision using data. What was the situation and how did you handle it?**

> So for the contract-to-date model which was mentioned earlier, there exists something called "temperature", which essentially is the percentage of the contract consumption till date (say ctd value) to the actual till date commited value (say prorated acr value). Now in the system the due to some backdating of a few contracts, the actual consumption starts way after than the starting date mentioned in the system. Now because of this, the ctd value comes from the actual consumption date while the prorated acr is something which is calculated based on system's starting dates. So due to different timelines, for these backdated contracts it used to show up a very lesser temperature than actual which used to worry the account managers as it seems like the customer is using much lesser than intended. So here I changed the methodology by convincing the stakeholders to make both the values to be calculated based on the actual consumption date itself and hence for regular contracts there is no impact and for backdated contracts it shows the real temperature based on actual usage. The other impact because of this exercise is that we got to know exactly what are the contracts getting backdated and flag them off so that over time the issue of backdating can be tracked with dates and how far they are backdated and ultimately reduce them.


**You mentioned convincing stakeholders — what was their initial reaction when you proposed changing the methodology? Was there pushback, and how did you get them to agree?**

> So even though on paper it seems like very straight forward, it took a real effort in convincing the stakeholders. So firstly there was a discussion to see if our contract-to-date model can state an calculated number for the backdated dates, which I firmly opposed due to the reason that even it shows something which is not there to be there. Also the fact that the committed revenue based on backdates is something which we are never gonna achieve as there is no consumption and it by itself is an inflated number. So comparing from actual consumption will be a better way. Their argument was that we won't be able to show the committed number being achieved, but the counter is that it is inflated and we can never achieve that under normal consumption anyways so it better to flag them than to make it seem real. Ultimately they agreed because the alternative was showing account managers a number that would always look bad for backdated contracts regardless of actual customer health. That's worse for everyone. And the side effect — being able to track and reduce backdating over time — was something they hadn't thought of but immediately saw value in.


**If you had to rebuild this pipeline today from scratch knowing what you know now — what would you do differently?**

> A few things. First, I'd invest more upfront in understanding the edge cases in the business logic — things like migration resets and backdated contracts. Those took significant debugging time mid-build because I didn't fully understand the business rules at the start. Second, I'd design the testing layer differently — right now tests caught upstream data issues well, but the proration bug slipped through because it was logically consistent but semantically wrong. I'd add more business-logic assertions earlier in the pipeline. And third, documentation — I started it late and it's been harder to onboard people as a result. I'd treat it as a first-class deliverable from day one, not something you do after the pipeline stabilises.


## Document Digisation Story

**Tell me about a time you built something from scratch with no clear requirements. How did you approach it?**
