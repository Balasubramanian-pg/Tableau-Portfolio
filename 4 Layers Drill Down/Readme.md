# Table of Contents

1. Purpose and outcome
2. Preparation and naming conventions
3. Build the four sheets (Year, Quarter, Month, Day)
    3.1 Create Sales by Year
    3.2 Duplicate to create Sales by Quarter
    3.3 Duplicate to create Sales by Month
    3.4 Duplicate to create Sales by Day
4. Create the Date Level parameter and per-sheet text fields
    4.1 Create `Date Level Parameter`
    4.2 Create the text helper fields on each sheet
5. Create Dynamic Zone Visibility Boolean calculations
6. Assemble the dashboard and wire zone visibility
7. Create parameter actions that drive the drill path (navigation)
8. Create parameter actions that drive filtering between levels
9. Create the single cross-sheet date filter calculation and apply it
10. Test and validate the drill flow
11. Optional polish and UX improvements
12. Troubleshooting checklist
13. Reasoning summary
14. ASSUMPTION and points that require verification or are uncertain

---

# 1 Purpose and outcome

This is a step by step, production ready procedure to implement a four level date drill down in Tableau. When complete you will be able to:

* Click a Year and show Quarters for that Year.
* Click a Quarter and show Months for that Quarter.
* Click a Month and show Days for that Month.
* Click a Day and return to Year level.

The interaction uses parameters, parameter actions, dynamic zone visibility, and a single shared date filter. Follow the names and formulas exactly for copy/paste ease.

---

# 2 Preparation and naming conventions

Use these exact names in the workbook so formulas and actions match the guide:

* Parameter names: `Date Level Parameter` and `Date Parameter`
* Sheet names: `Sales by Year`, `Sales by Quarter`, `Sales by Month`, `Sales by Day`
* Calculated fields and helper fields: `Year Text`, `Quarter Text`, `Month Text`, `Day Text`, `Show Year`, `Show Quarter`, `Show Month`, `Show Day`, `Date Filter`
* Dashboard name: `Date Drill Dashboard`

Keeping names consistent avoids errors when wiring actions and filters.

---

# 3 Build the four sheets (Year, Quarter, Month, Day)

## 3.1 Create Sales by Year

1. Connect to the Superstore sample or your date-enabled dataset.
2. Right click `Order Date` in the Data pane. Drag it to Columns and choose `Continuous` → `YEAR`.
3. Drag `SUM([Sales])` to Rows.
4. Rename the sheet to `Sales by Year`.
5. Format axes and labels as you prefer.

## 3.2 Duplicate to create Sales by Quarter

1. Right click the `Sales by Year` sheet tab and choose Duplicate.
2. On the Columns shelf click the plus sign next to YEAR to expand to QUARTER.
3. Rename this sheet to `Sales by Quarter`.
4. Adjust formatting or axis granularity if needed.

## 3.3 Duplicate to create Sales by Month

1. Right click `Sales by Quarter` and choose Duplicate.
2. On the Columns shelf click the plus sign next to QUARTER to expand to MONTH.
3. Rename this sheet to `Sales by Month`.
4. Verify months show correctly for quarters.

## 3.4 Duplicate to create Sales by Day

1. Right click `Sales by Month` and choose Duplicate.
2. On the Columns shelf click the plus sign next to MONTH to expand to DAY.
3. If needed, click the plus again to switch to exact day granularity rather than week.
4. Rename this sheet to `Sales by Day`.
5. Verify daily bars or marks are sensibly aggregated.

Note: using Continuous date parts yields a continuous timeline. If your visual requires discrete labels change the pill type accordingly. The instructions above assume continuous date parts to preserve the expand plus controls.

---

# 4 Create the Date Level parameter and per-sheet text fields

## 4.1 Create `Date Level Parameter`

1. In the Data pane click the drop down and choose Create Parameter.
2. Name: `Date Level Parameter`.
3. Data type: String.
4. Current value: set to `Year`.
5. Click OK.
6. You do not need to show the parameter control on the dashboard. It will be driven by parameter actions.

## 4.2 Create the text helper fields on each sheet

These are small calculated fields that return a fixed string. They are used as the field passed into the parameter action.

1. On `Sales by Day` create a calculated field named `Year Text` with formula:

   ```
   "Year"
   ```

   Place `Year Text` on Detail for `Sales by Day`. Right click the pill and uncheck Include in Tooltip.

2. On `Sales by Month` create a calculated field named `Day Text` with formula:

   ```
   "Day"
   ```

   Place `Day Text` on Detail for `Sales by Month`. Uncheck Include in Tooltip.

3. On `Sales by Quarter` create `Month Text`:

   ```
   "Month"
   ```

   Place on Detail and uncheck Include in Tooltip.

4. On `Sales by Year` create `Quarter Text`:

   ```
   "Quarter"
   ```

   Place on Detail and uncheck Include in Tooltip.

Rationale: when the user clicks a mark in a sheet we will pass the corresponding string into `Date Level Parameter` so the dashboard knows which chart to show next.

---

# 5 Create Dynamic Zone Visibility Boolean calculations

Create four Boolean calculated fields that return True when the `Date Level Parameter` matches the corresponding text.

1. Create `Show Year`:

   ```
   [Date Level Parameter] = "Year"
   ```

2. Create `Show Quarter`:

   ```
   [Date Level Parameter] = "Quarter"
   ```

3. Create `Show Month`:

   ```
   [Date Level Parameter] = "Month"
   ```

4. Create `Show Day`:

   ```
   [Date Level Parameter] = "Day"
   ```

These are case sensitive. Type the strings exactly as used in the text helper fields and parameter default.

---

# 6 Assemble the dashboard and wire zone visibility

1. Create a new dashboard and name it `Date Drill Dashboard`.
2. Drag a Vertical Container onto the canvas. The four sheets must be inside the same container for smooth swapping.
3. Drag `Sales by Year`, `Sales by Quarter`, `Sales by Month`, `Sales by Day` into that container in that order or any order you prefer. They must be siblings in the same container.
4. Select `Sales by Day` in the layout tree. In the Layout pane check Control Visibility Using and select `Show Day`. The sheet will hide because `Date Level Parameter` currently equals `Year`.
5. Select `Sales by Month` and set Control Visibility Using to `Show Month`.
6. Select `Sales by Quarter` and set Control Visibility Using to `Show Quarter`.
7. Select `Sales by Year` and set Control Visibility Using to `Show Year`. `Sales by Year` will be visible initially because the parameter default is `Year`.

Result: only the sheet matching the parameter value is visible at any time.

---

# 7 Create parameter actions that drive the drill path (navigation)

We will create four parameter change actions that change `Date Level Parameter` when the user clicks on a mark at a given level. These actions are the navigation controls.

1. From the Dashboard menu choose Actions.

2. Click Add Action > Change Parameter. Configure the first action:

   * Name: `Show Quarter`
   * Source Sheet: `Sales by Year`
   * Run action on: Select
   * Target Parameter: `Date Level Parameter`
   * Value: select the field `Quarter Text`
   * Clearing the selection: set to `Year` or Blank depending on desired reset behavior. Using `Year` or Blank both work. If you want clicking outside to return to Year use Blank.
   * Click OK.

3. Add second action:

   * Name: `Show Month`
   * Source Sheet: `Sales by Quarter`
   * Target Parameter: `Date Level Parameter`
   * Value: `Month Text`
   * Run on: Select
   * Clearing behavior: Blank or `Year`. Click OK.

4. Add third action:

   * Name: `Show Day`
   * Source Sheet: `Sales by Month`
   * Target Parameter: `Date Level Parameter`
   * Value: `Day Text`
   * Run on: Select
   * Clearing behavior: Blank or `Year`. Click OK.

5. Add fourth action:

   * Name: `Show Year`
   * Source Sheet: `Sales by Day`
   * Target Parameter: `Date Level Parameter`
   * Value: `Year Text`
   * Run on: Select
   * Clearing behavior: Blank or `Year`. Click OK.

6. Click OK to close the Actions dialog.

Behavior: clicking a Year sets parameter to `Quarter` so the quarters sheet becomes visible. Clicking a Quarter sets parameter to `Month`, and so on. Clicking a Day sets parameter to `Year` so the dashboard resets.

---

# 8 Create parameter actions that drive filtering between levels

The navigation parameter shows the right chart but does not yet filter descendants to the selected date span. Create second group of parameter actions that populate a `Date Parameter` used to filter the lower level sheets.

## 8.1 Create `Date Parameter`

1. Create a parameter named `Date Parameter`.
2. Data type: Date.
3. Current value: leave blank or set to a sensible default.
4. Click OK.

## 8.2 Add parameter actions to populate `Date Parameter`

From Dashboard > Actions add three Change Parameter actions for filtering:

1. Action `Date Filter Year`:

   * Source Sheet: `Sales by Year`
   * Target Parameter: `Date Parameter`
   * Value: choose the field `Order Date` truncated at YEAR. If the action dialog requires a field, create a helper calculated field on `Sales by Year` with formula:

     ```
     DATETRUNC('year', [Order Date])
     ```

     and pass that field.
   * Run on: Select
   * Clearing behavior: Blank or Null. Click OK.

2. Action `Date Filter Quarter`:

   * Source Sheet: `Sales by Quarter`
   * Target Parameter: `Date Parameter`
   * Value: use a helper field:

     ```
     DATETRUNC('quarter', [Order Date])
     ```
   * Run on: Select
   * Click OK.

3. Action `Date Filter Month`:

   * Source Sheet: `Sales by Month`
   * Target Parameter: `Date Parameter`
   * Value: helper field:

     ```
     DATETRUNC('month', [Order Date])
     ```
   * Run on: Select
   * Click OK.

Note: You do not need a Date Filter action for Day because drilling to Day should set context via the Month action, and Day clicks are used to reset to Year. If you want a Day to populate a date param for very precise filtering create `DATETRUNC('day', [Order Date])` and pass it from `Sales by Day`.

---

# 9 Create the single cross-sheet date filter calculation and apply it

Create one calculated field to use as a filter across quarter, month, and day views.

## 9.1 Create `Date Filter` calculation

1. On `Sales by Quarter` create a calculated field named `Date Filter` with this logic:

```
IF [Show Quarter] THEN
    IF DATETRUNC('year', [Order Date]) = DATETRUNC('year', [Date Parameter])
    THEN "T" END
ELSEIF [Show Month] THEN
    IF DATETRUNC('quarter', [Order Date]) = DATETRUNC('quarter', [Date Parameter])
    THEN "T" END
ELSEIF [Show Day] THEN
    IF DATETRUNC('month', [Order Date]) = DATETRUNC('month', [Date Parameter])
    THEN "T" END
END
```

2. Click OK.

## 9.2 Apply `Date Filter` to the appropriate sheets

1. On `Sales by Quarter` drag `Date Filter` to Filters and select `T`.
2. Right click the `Date Filter` pill on Filters and choose Apply to Worksheets > Selected Worksheets.
3. Select `Sales by Quarter`, `Sales by Month`, and `Sales by Day` and click OK.

Explanation: When the dashboard is at Quarter level the `Date Filter` keeps only the quarters that belong to the year stored in `Date Parameter`. When at Month level it keeps only months that belong to the selected quarter, and so on.

---

# 10 Test and validate the drill flow

Follow this validation sequence exactly to confirm correct behavior.

1. Ensure `Date Level Parameter` default is `Year`. The dashboard initially shows yearly view.
2. Click a Year on `Sales by Year`. Expected: dashboard shows `Sales by Quarter` for that Year. Quarters should be the four quarters of the selected Year.
3. Click a Quarter. Expected: dashboard shows `Sales by Month` for that Quarter. Months should belong to the selected Quarter and Year.
4. Click a Month. Expected: dashboard shows `Sales by Day` for that Month. Daily marks should belong to the selected month.
5. Click a Day. Expected: dashboard returns to Year level.
6. While drilling, verify that the `Date Parameter` value is set and that `Date Filter` is applied to descendant sheets so children show only within the chosen parent.
7. Test clearing selection behavior for parameter actions. Clicking blank space should reset if you configured clearing to Blank. Otherwise it will keep last value.

If any step fails, consult the Troubleshooting checklist in section 12.

---

# 11 Optional polish and UX improvements

1. Hide axis titles and trim tick marks to reduce visual clutter.
2. Add a breadcrumb text object that shows current `Date Parameter` and `Date Level Parameter` using a calculated display field bound to a text worksheet or dynamic title. Example calc `Current Context`:

   ```
   [Date Level Parameter] + " : " + STR(DATETRUNC('month', [Date Parameter]))
   ```

   Adjust formatting per level.
3. Add a Reset button: create a small worksheet labeled Reset and add a Change Parameter action that sets `Date Level Parameter` to `Year` and clears `Date Parameter`.
4. Format tooltips to display the exact date range and measure.
5. Use color or reference lines to highlight the selected period.
6. Limit initial data volume with context filters or extracts on large datasets.

---

# 12 Troubleshooting checklist

* Problem: Nothing happens when I click a Year.

  * Verify the `Show Quarter` parameter action exists, targets `Date Level Parameter`, and uses `Quarter Text` as the value.
  * Confirm action Run On is set to Select.
* Problem: Quarters show but are not limited to the chosen Year.

  * Verify the `Date Filter` calculation logic and that `Date Parameter` is populated by the `Date Filter Year` action.
  * Confirm `Date Filter` is applied to the Quarter, Month, and Day worksheets.
* Problem: Month level never appears.

  * Confirm the `Show Month` parameter action is present, targets `Date Level Parameter`, and is driven by `Sales by Quarter` with `Month Text`.
* Problem: Filters behave inconsistently after changing parameter clearing settings.

  * Review each Change Parameter action clearing behavior. Setting Clearing to Blank typically provides a clean reset.
* Problem: Text helper fields appear in Tooltips.

  * Ensure you unchecked Include in Tooltip for each text helper.
* Problem: Performance slow on Day view.

  * Consider using an extract or pre-aggregating the data for daily level, or add initial context filters.

---

# 13 Reasoning summary

The implementation separates navigation from filtering. `Date Level Parameter` controls which sheet is visible via dynamic zone visibility. Per-sheet text helper fields are used to pass the target level into that parameter with Change Parameter actions. `Date Parameter` stores the actual date period selected and is populated by secondary Change Parameter actions. A single `Date Filter` calculated field uses `Date Parameter` together with the active level to restrict descendant sheets to the correct parent scope. This design keeps visual swapping and filtering decoupled and predictable.

---

# 14 ASSUMPTION and points that require verification or are uncertain

* ASSUMPTION: You are using Tableau Desktop version that supports Dynamic Zone Visibility and parameter actions. These features exist in Tableau 2022.2 and newer, though parameter actions exist earlier. Verify your version.
* ASSUMPTION: Field names are `Order Date` and `Sales`. If your fields differ, substitute them in helper formulas and date truncations.
* Verification recommended: Behavior of Clearing Selection for parameter actions can vary slightly by Tableau patch. Test the clearing behavior and adjust to Blank or a default string as desired.
* Verification recommended: If the workbook uses multiple data sources or data blending, DATETRUNC and parameter action behavior may differ. Test cross-source behavior.
* Verification recommended: For very large datasets, Day level may be slow. Consider extracts or pre-aggregations.

---

If you want, I will now:

1. Produce exact copyable calculated field code for the helper fields and `Date Filter` with variations for different date truncation strategies.
2. Create a dashboard blueprint listing container positions, sizes, and the complete Actions dialog values as a compact checklist you can follow in Tableau step by step.
3. Build a debug checklist that prints the current parameter values to the dashboard for troubleshooting.
