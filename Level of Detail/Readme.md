# Table of Contents

1. Purpose and expected outcome
2. Preparation and naming conventions
3. Use Case 1 Customer order frequency <br>
    3.1 Goal and explanation <br>
    3.2 Step by step build (fixed LOD + histogram) <br>
    3.3 Visual permutations and validation <br>
    3.4 Troubleshooting and notes <br>
4. Use Case 2 Cohort analysis (first purchase year cohorts) <br>
    4.1 Goal and explanation <br>
    4.2 Step by step LOD build and cohort matrix <br>
    4.3 How to answer “how many 2018 cohort customers bought in 2020” <br>
    4.4 Troubleshooting and notes <br> 
5. Use Case 3 Daily profit KPI (profitable vs unprofitable days) <br>
    5.1 Goal and explanation <br>
    5.2 Step by step LOD build and tagging logic <br>
    5.3 Summary view, detail view and interactive filtering <br>
    5.4 Precision issues and validation <br>
6. Use Case 4 Percent of total with LOD vs table calculation <br>
    6.1 Goal and explanation of difference <br>
    6.2 Step by step LOD fields for grand total and subtotal by region <br>
    6.3 How to format and test behavior under filters <br>
    6.4 EXCLUDE variant and when it behaves differently <br>
7. Use Case 5 New customer acquisition (first order date trend) <br>
    7.1 Goal and explanation <br>
    7.2 Step by step LOD build and time series visualization <br>
    7.3 Running total variant and segmentation <br>
8. General validation checklist across all use cases <br>
9. Performance, best practices and maintainability <br>

# 1 Purpose and expected outcome

This document turns the spoken walkthrough into precise, copyable, step by step Tableau instructions for the first five practical LOD use cases: customer order frequency, cohort analysis, daily profit KPI, percent of total (LOD versus table calculation), and new customer acquisition. Each use case contains exact calculated field code, where to place fields on the worksheet, how to build the visuals, and how to validate results.

# 2 Preparation and naming conventions

Follow these names so formulas and steps work with minimal substitution. If your data uses different field names, replace consistently.

* Fields assumed present: `Customer ID`, `Order ID`, `Order Date`, `Sales`, `Profit`, `Region`, `Segment`
* Recommended calculated field prefixes: `LOD_` for LOD expressions, `FIXED_` for fixed LODs, `Tag_` for simple tagging fields
* Recommended sheets: `Orders Frequency`, `Orders Frequency Histogram`, `Cohort Matrix`, `Daily Profit Summary`, `Daily Profit Details`, `PercentOfTotal_Map`, `Acquisition Trend`

Work in Tableau Desktop connected to your dataset (Superstore or equivalent) before starting.

# 3 Use Case 1 Customer order frequency

## 3.1 Goal and explanation

Compute how many times each customer has ordered (order frequency), then show distribution of customers by frequency (for example count of customers who ordered 1 time, 2 times, 3 times, etc.). Use a FIXED LOD so each customer’s order count is computed at customer granularity regardless of the current viz level.

## 3.2 Step by step build (fixed LOD + histogram)

1. Create LOD field that counts orders per customer.

   * Name: `FIXED_Order_Count_Per_Customer`
   * Formula:

     ```
     { FIXED [Customer ID] : COUNTD([Order ID]) }
     ```
   * Click OK.

2. Build a table that lists customers and their frequency (for verification).

   * Sheet: `Orders Frequency`
   * Drag `Customer ID` to Rows.
   * Drag `FIXED_Order_Count_Per_Customer` to Text (or Label).
   * Optional: Sort by `FIXED_Order_Count_Per_Customer` descending.

3. Create a histogram showing number of customers per frequency value using the LOD as a dimension. Two approaches follow.

### Approach A as dimension (discrete distribution)

* Right click `FIXED_Order_Count_Per_Customer` in the Data pane and choose Convert to Dimension (if Tableau treats it as measure).
* Drag `FIXED_Order_Count_Per_Customer` to Columns.
* Drag `Customer ID` to Rows and change to `COUNTD(Customer ID)` or drag `Customer ID` to Text and right-click choose Count Distinct.
* This yields a bar for each frequency value present in the data.

### Approach B using bins (complete integer axis)

* Duplicate `FIXED_Order_Count_Per_Customer` (right click Duplicate or create new bin).
* Right click the duplicate and choose Create > Bins.
* Set Bin size to 1. Click OK. A new bin field appears.
* Use the bin on Columns and `COUNTD(Customer ID)` on Rows. This produces bars for every integer frequency including values that are missing in raw categorical distribution because bins produce a continuous bucket axis.

4. Show both versions side by side on a dashboard to compare the “dimension” method versus binned method.

## 3.3 Visual permutations and validation

* Validation step A: confirm total customers sum equals `COUNTD(Customer ID)`.

  * Add totals from Analytics pane or compute grand total.
* Validation step B: to answer “how many of the 5 times repeat customers bought in 2020”

  * Create a filter for `Order Date` year = 2020 on the worksheet and observe the count intersection for frequency = 5.
* Tip: converting the LOD value to continuous and using bars may give a filled axis for missing integers. Use bar mark and adjust size.

## 3.4 Troubleshooting and notes

* If the LOD returns unexpected numbers, check that `COUNTD([Order ID])` is the desired aggregation. If each order id may duplicate under certain blends, ensure primary key uniqueness.
* If you remove `Customer ID` from the view and lose detail, remember the LOD computed per customer stays available as a field. Use the LOD field as a dimension or bin to aggregate customers.

# 4 Use Case 2 Cohort analysis (first purchase year cohorts)

## 4.1 Goal and explanation

Assign each customer to the cohort defined by the year of their first purchase. Then build a cohort matrix that shows how members of each cohort behave in subsequent years. Use a FIXED LOD to compute the first purchase year per customer.

## 4.2 Step by step LOD build and cohort matrix

1. Create cohort LOD field.

   * Name: `FIXED_Cohort_Year`
   * Formula:

     ```
     { FIXED [Customer ID] : YEAR(MIN([Order Date])) }
     ```
   * Click OK. This returns the first order year per customer.

2. Build the cohort matrix.

   * Sheet: `Cohort Matrix`
   * Drag `FIXED_Cohort_Year` to Rows (discrete).
   * Drag `YEAR([Order Date])` to Columns (discrete year of current purchases).
   * Drag `Customer ID` to Text or Rows and change to `COUNTD(Customer ID)`.
   * Add Totals via Analytics pane if desired.

3. Add filters for drill down.

   * Show filter for `FIXED_Cohort_Year` and for `YEAR([Order Date])` so you can select cohort or observation year.

## 4.3 How to answer “how many 2018 cohort customers bought in 2020”

* With `FIXED_Cohort_Year` on Rows and `YEAR([Order Date])` on Columns, find the intersection cell where Row = 2018 and Column = 2020. The value in that cell is `COUNTD(Customer ID)` for customers whose first purchase year was 2018 and who had purchases in 2020.

## 4.4 Troubleshooting and notes

* Ensure `FIXED_Cohort_Year` is a dimension for placement in rows.
* If counts look off when filters are applied, remember LOD FIXED is computed before dimension filters unless filters are moved to context. If you need cohort to respect cohort filters you added, put those filters into context or use different LOD logic. See section 11 for important notes about filter order.

# 5 Use Case 3 Daily profit KPI (profitable vs unprofitable days)

## 5.1 Goal and explanation

Tag each calendar day as profitable if total profit for that day is positive, else unprofitable. Use a FIXED LOD to compute per-day profit and then classify days. Count distinct days in each tag and show trend over time. Using LOD prevents losing per-day granularity when you aggregate.

## 5.2 Step by step LOD build and tagging logic

1. Create fixed LOD for day profit.

   * Name: `FIXED_Profit_Per_Day`
   * Formula:

     ```
     { FIXED DATETRUNC('day', [Order Date]) : SUM([Profit]) }
     ```
   * Click OK.

2. Create a tag field that labels a day profitable or not.

   * Name: `Tag_Profitable_Day`
   * Formula:

     ```
     IF [FIXED_Profit_Per_Day] > 0 THEN "Profitable"
     ELSE "Not Profitable" END
     ```
   * Click OK.

3. Build a summary count of days by tag.

   * Sheet: `Daily Profit Summary`
   * Drag `Tag_Profitable_Day` to Columns.
   * Drag `Order Date` to Rows and convert to discrete day if you want detail. For summary count: drag `Order Date` to Text and change to `COUNTD(DATETRUNC('day', [Order Date]))` or drag `Order Date` to Rows and right-click choose Count Distinct.
   * Alternatively place `COUNTD(DATETRUNC('day', [Order Date]))` on Rows and `Tag_Profitable_Day` on Columns.

4. Build a details sheet for validation.

   * Sheet: `Daily Profit Details`
   * Drag `DATETRUNC('day', [Order Date])` to Rows.
   * Drag `SUM([Profit])` and `FIXED_Profit_Per_Day` to Text to confirm they match.
   * Drag `Tag_Profitable_Day` to Color.

## 5.3 Summary view, detail view and interactive filtering

* Combine the summary and details on a dashboard.
* Add a filter action: clicking the “Not Profitable” bar filters the details to show only days tagged Not Profitable. Use a Dashboard > Actions > Filter.

## 5.4 Precision issues and validation

* If some values appear as zero but are actually small positive or negative numbers, increase numeric display precision to 5 decimal places: right click measure > Format > Numbers > set decimal places. The zero might be a rounded value.
* Sort within the detail view to verify the most negative days appear at top.

# 6 Use Case 4 Percent of total with LOD vs table calculation

## 6.1 Goal and explanation of difference

Table calculation percent of total is computed at the view level and therefore responds to interactive filtering by recomputing denominator across visible marks. A FIXED LOD grand total gives you a denominator that does not change when dimension filters are applied, so percent of grand total remains stable under those filters.

## 6.2 Step by step LOD fields for grand total and subtotal by region

1. Grand total via FIXED LOD (table scope). Two equivalent styles are shown.

   Option A explicit FIXED:

   * Name: `LOD_GrandTotal_Fixed`
   * Formula:

     ```
     { FIXED : SUM([Sales]) }
     ```

     Click OK.

   Option B simplified table scoped aggregation (works identically):

   * Name: `LOD_GrandTotal_Simple`
   * Formula:

     ```
     SUM([Sales])
     ```

     This is not a LOD expression but is useful when placed in a calculation that forces table scope. The best practice is still to use FIXED to be explicit.

2. Subtotal by region using FIXED:

   * Name: `LOD_Subtotal_Region`
   * Formula:

     ```
     { FIXED [Region] : SUM([Sales]) }
     ```
   * Click OK.

3. Percent of grand total:

   * Name: `Calc_Pct_Of_Grand`
   * Formula:

     ```
     SUM([Sales]) / [LOD_GrandTotal_Fixed]
     ```
   * Format as percentage.

4. Percent of region total:

   * Name: `Calc_Pct_Of_Region`
   * Formula:

     ```
     SUM([Sales]) / [LOD_Subtotal_Region]
     ```
   * Format as percentage.

## 6.3 How to format and test behavior under filters

* Build a map or table with `State` or `Region` and add `Calc_Pct_Of_Grand` to Tooltip or Label.
* Add a filter such as `Segment`. Toggle filter values. Observe:

  * `Calc_Pct_Of_Grand` remains constant because `LOD_GrandTotal_Fixed` ignores dimension filters.
  * Table calc percent of total recomputes across filtered marks and will adjust denominators.

## 6.4 EXCLUDE variant and when it behaves differently

* EXCLUDE computes after some dimensions in the view but is still affected by dimension filters that are not context filters. Example:

  ```
  { EXCLUDE [Region] : SUM([Sales]) }
  ```

  * This will give totals with `Region` excluded but it will still be affected by regular dimension filters. FIXED is evaluated before dimension filters except context filters. Use FIXED if you need stabilization against filtering, or use context filters deliberately to change FIXED behavior.

* Validation: add a segment filter and observe that EXCLUDE-based numbers change while FIXED numbers do not.

# 7 Use Case 5 New customer acquisition (first order date trend)

## 7.1 Goal and explanation

Identify the first purchase date for each customer and plot how many customers were acquired over time. LOD FIXED by customer returns the first order date per customer. Aggregate first-order dates into weeks or months and count customers acquired in each period.

## 7.2 Step by step LOD build and time series visualization

1. First order date per customer via FIXED LOD:

   * Name: `FIXED_First_Order_Date`
   * Formula:

     ```
     { FIXED [Customer ID] : MIN([Order Date]) }
     ```
   * Click OK.

2. Build acquisition time series:

   * Sheet: `Acquisition Trend`
   * Drag `FIXED_First_Order_Date` to Columns and set it to the desired date truncation: e.g., right click > More > Custom > choose Week or use `DATETRUNC('week', [FIXED_First_Order_Date])` in a calculated field for precise control.
   * Drag `Customer ID` to Rows and change to `COUNTD(Customer ID)`.
   * This shows number of new customers acquired per week.

3. Add a running total variant:

   * Duplicate the `COUNTD(Customer ID)` pill on Rows. On the duplicate, right click > Quick Table Calculation > Running Total. This shows cumulative customers acquired over time.

## 7.3 Running total variant and segmentation

* Add `Segment` or `Region` to Color to compare acquisition by segment.
* Add tooltips and annotations for spikes.

# 8 General validation checklist across all use cases

* Confirm each LOD field returns expected values by placing it on a detail table next to raw records.
* For FIXED LOD: verify how filters affect the field. If you expect the LOD to respect a dimension filter, move that filter to context.
* For COUNTD behaviors across period intersections, use matrices and totals to confirm sums.
* Check display precision for measures to avoid apparent zeros. Increase decimal places when necessary.
* When mixing LODs and table calculations, document calculation order and dependencies in workbook notes.

# 9 Performance, best practices and maintainability

* Prefer extracts for very large datasets when computing many LODs at runtime.
* Keep LODs readable. Example: use descriptive names such as `FIXED_First_Order_Date_By_Customer` instead of obscure names.
* Avoid nesting many heavy LODs in a single calculation. Break into intermediate fields if needed.
* Use context filters intentionally to control whether FIXED LODs are affected by a filter. Putting a filter into context makes FIXED respect that filter; leaving it out makes the FIXED ignore it.
* Document assumptions in the workbook: primary keys, data freshness, timezone considerations, and date grain.
