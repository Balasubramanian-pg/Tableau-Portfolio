# Table of Contents

1. Overview
2. Preparation and naming conventions
3. Create the Level parameters
    3.1 Create Level 1 Parameter
    3.2 Create Level 2 Parameter
4. Build the Level 1 calculated field (controls first drill level)
5. Add the Level 1 parameter action (click to drill into Sub-Category)
6. Create Level 1 header calculated field (optional visual header)
7. Create Level 2 calculated field (controls second drill level)
8. Add the Level 2 parameter action (click Sub-Category to drill into Region)
9. Prevent persistent highlight using a highlight action
10. Create color logic for levels and apply colors
11. Final formatting, sorting, and polish
12. Validation and testing checklist
13. Troubleshooting tips
14. Reasoning summary
15. ASSUMPTION and points that require verification or are uncertain

# 1 Overview

This is a step by step, copy-and-paste ready guide to implement a two level drill down in Tableau using parameter actions and calculated fields. The solution reproduces the exact flow in the source transcript: Category → Sub-Category → Region, with visual headers, highlight control, and color changes per level. Use this procedure inside Tableau Desktop.

# 2 Preparation and naming conventions

Follow these naming conventions exactly to keep formulas simple and consistent:

* Parameters: `Level 1 Parameter`, `Level 2 Parameter`
* Calculated fields: `Level 1`, `Level 1 Header`, `Level 2`, `Highlight`, `Level 1 Color`, `Level 2 Color`, `Rank` (optional)
* Worksheets: `Drill Sheet` (single worksheet that will show all three levels)
* Dashboard: `Drill Dashboard`

Using these names lets you copy formulas without renaming.

# 3 Create the Level parameters

## 3.1 Create Level 1 Parameter

1. In the Data pane, click the triangle and choose Create Parameter.
2. Name: `Level 1 Parameter`
3. Data type: String
4. Allowable values: All (default) or List if you prefer to preload values.
5. Current value: leave blank.
6. Click OK.
7. Right click the parameter and choose Show Parameter if you want a visible control for debugging. Remove the control later if you want click only behavior.

## 3.2 Create Level 2 Parameter

1. Repeat the same steps: Create Parameter.
2. Name: `Level 2 Parameter`
3. Data type: String
4. Allowable values: All or List.
5. Current value: leave blank.
6. Click OK.
7. Optionally Show Parameter for debugging.

# 4 Build the Level 1 calculated field (controls first drill level)

Create a calculated field named `Level 1` that returns the appropriate value to place on Rows. Exact formula:

```
IF [Category] = [Level 1 Parameter] THEN
    [Sub-Category]
ELSE
    [Category]
END
```

Steps to create and use it:

1. Data pane > triangle > Create Calculated Field.
2. Paste the formula above.
3. Click OK.
4. Drag `Level 1` to Rows on `Drill Sheet`.
5. Put `SUM([Sales])` on Columns or your chosen measure.

Explanation: when `Level 1 Parameter` matches a Category, the row shows Sub-Category values. Otherwise the Category appears at that row position. This creates a single column that can show Category or Sub-Category values contingent on the parameter.

# 5 Add the Level 1 parameter action (click to drill into Sub-Category)

Create a parameter action that assigns Category to `Level 1 Parameter` on click.

Steps:

1. On the Worksheet menu select Actions.
2. Click Add Action > Change Parameter.
3. Name the action: `Parameter Level 1`.
4. Source Sheet: select `Drill Sheet` (or the sheet where users will click).
5. Run action on: Select.
6. Target Parameter: `Level 1 Parameter`.
7. Value: choose field `Category`.
8. Clearing the selection: set to Blank (or set to Default if you want a default). Choosing Blank collapses back to top level on clearing.
9. Click OK to save.
10. Click OK to close the Actions dialog.

Behavior: clicking a Category value populates `Level 1 Parameter` with that category and causes the `Level 1` calculated field to return Sub-Category rows for that category.

# 6 Create Level 1 header calculated field (optional visual header)

This calculation shows the selected Category as a header row for context.

Formula for `Level 1 Header`:

```
IF [Category] = [Level 1 Parameter] THEN
    [Category]
ELSE
    ""
END
```

Steps:

1. Create calculated field as above.
2. Drag `Level 1 Header` to Rows and position it between the `Level 1` and other fields if you will display multiple columns.
3. Right click the header, choose Rotate Label if you want vertical header text.
4. Hide field labels for rows if desired: right click Field Labels > Hide Field Labels for Rows.

Behavior: when a Category is selected, `Level 1 Header` displays that category as a header; otherwise the field is blank.

# 7 Create Level 2 calculated field (controls second drill level)

Create `Level 2` to return Region values when Sub-Category is selected, else blank.

Formula for `Level 2`:

```
IF [Sub-Category] = [Level 2 Parameter] THEN
    [Region]
ELSE
    ""
END
```

Steps:

1. Create the calculated field above and name it `Level 2`.
2. Drag `Level 2` to Rows under `Level 1` and `Level 1 Header` so the hierarchy reads: Level 1 Header, Level 1, Level 2.
3. Place your measure `SUM([Sales])` on Columns if not already present.

Explanation: this shows Regions only when a Sub-Category has been selected into `Level 2 Parameter`.

# 8 Add the Level 2 parameter action (click Sub-Category to drill into Region)

Create a second parameter action that assigns the selected Sub-Category into `Level 2 Parameter`.

Steps:

1. Worksheet menu > Actions.
2. Add Action > Change Parameter.
3. Name it: `Parameter Level 2`.
4. Source Sheet: `Drill Sheet`.
5. Run action on: Select.
6. Target Parameter: `Level 2 Parameter`.
7. Value: choose field `Sub-Category`.
8. Clearing the selection: set to Blank.
9. Click OK and close Actions dialog.

Behavior: after selecting a Category (which populates `Level 1 Parameter`), clicking a Sub-Category will populate `Level 2 Parameter` and cause `Level 2` to display Region values for that subcategory.

Note: if you want clicking a Region to reset the drill, create a third parameter action that targets `Level 1 Parameter` and sets it to Blank on selection of Regions.

# 9 Prevent persistent highlight using a highlight action

By default clicking marks leaves the selected mark highlighted. To avoid last click remaining highlighted across levels, add a dedicated highlight action that only uses a dummy field.

Steps:

1. Create a calculated field named `Highlight` with contents:

```
"Highlight"
```

2. Drag `Highlight` to the Detail shelf on the Marks card.
3. Worksheet menu > Actions.
4. Add Action > Highlight.
5. Name it: `Target Highlighting`.
6. Source Sheet: `Drill Sheet`.
7. Target Sheet: `Drill Sheet` or other sheets you want to control.
8. Under Target Highlighting, check only `Highlight`.
9. Run action on: Select or Hover depending on your UX. Select works for click behavior.
10. Click OK.

Effect: because the only field used for target highlighting is `Highlight` which contains the same constant for all marks, Tableau will not preserve the appearance of a single last selected bar, and the visual looks consistent as you drill.

# 10 Create color logic for levels and apply colors

Create two color calculations to change mark color as the user drills.

## 10.1 Level 1 Color calculation

```
[Category] = [Level 1 Parameter]
```

Name: `Level 1 Color`. Drag this field to Color on the Marks card.

## 10.2 Level 2 Color calculation

```
[Sub-Category] = [Level 2 Parameter]
```

Name: `Level 2 Color`. Drag this to Detail, then click the pill ellipsis on the Marks card and choose Color. Configure color assignments or create a combined color logic if needed.

Optional combined color field to drive a single color shelf:

```
IF [Sub-Category] = [Level 2 Parameter] THEN "Level 2 Selected"
ELSEIF [Category] = [Level 1 Parameter] THEN "Level 1 Selected"
ELSE "Base"
END
```

Name: `Drill Color`. Put `Drill Color` onto Color and assign distinct colors for "Level 2 Selected", "Level 1 Selected", and "Base".

Explanation: Level 1 selection highlights its child subcategories with one color; Level 2 selection highlights regions with another color.

# 11 Final formatting, sorting, and polish

1. Sort rows by `SUM([Sales])` descending to maintain consistent ordering.
2. Add `Rank` if desired: create calculated field `Rank` with `RANK(SUM([Sales]))` and put on Label.
3. Format tooltips: edit Tooltip to show Category, Sub-Category, Region, Sales, and Rank.
4. Adjust axis, gridlines, and fonts for readability.
5. Tweak colors and legends.
6. Optionally add reference lines or KPI cards to the dashboard.
7. Save workbook and publish if needed.

# 12 Validation and testing checklist

* Click a Category. Expected: `Level 1 Parameter` is set and Sub-Category rows appear under the selected Category.
* Click another Category. Expected: Sub-Category list updates for new category.
* Click a Sub-Category. Expected: `Level 2 Parameter` is set and Region rows appear for that Sub-Category.
* Click a Region when at Level 2. Expected: selection clears or returns to top level if you implemented a reset.
* Verify colors change for Level 1 and Level 2 selections.
* Verify highlight action removes persistent highlighting.
* Verify headers show the selected Category via `Level 1 Header`.
* Confirm tooltips show expected context.

# 13 Troubleshooting tips

* If clicking does nothing: confirm the action is added to the correct worksheet and Run Action On is set to Select.
* If the sheet never returns to top level: check clearing selection behavior on parameter actions. Set to Blank to allow reset.
* If Level 2 never shows: confirm that `Level 2` calc compares the correct field to `Level 2 Parameter` and that `Level 2 Parameter` receives Sub-Category values.
* If colors do not change: verify the fields on Color or Detail and check for conflicting color assignments.
* If headers show NULL or blank text: ensure your header calc returns empty string `""` not NULL. Use `""` for blank text.
* If performance slows on large datasets: consider extracts or limiting initial rows with context filters.

# 14 Reasoning summary

Steps were derived from the provided transcript and organized into clear, numbered instructions. The approach uses two string parameters and parameter actions to capture user clicks, calculated fields to map parameter values into display logic, and a highlight action to control mark selection appearance. Color fields are calculated to visually distinguish drill levels. The method places all logic inside a single worksheet so the dashboard can present a compact drill user experience.

# 15 ASSUMPTION and points that require verification or are uncertain

* ASSUMPTION: You are using a Tableau Desktop release that supports parameter actions and dynamic visibility of calculated results. If you use an older release, parameter action UI and behavior may differ.
* ASSUMPTION: Data fields are named exactly `Category`, `Sub-Category`, `Region`, and `Sales`. If your field names differ, substitute them in formulas.
* Verification recommended: Clearing selection behavior may vary based on exact Tableau patch level. Test clearing selection behavior in your version and adjust action settings accordingly.
* Verification recommended: If your workbook uses multiple data sources or blends, parameter actions may behave differently. Test interactions when multiple sources are present.
