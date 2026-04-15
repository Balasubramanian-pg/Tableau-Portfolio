# 1. Table of contents

1. Purpose
2. Executive summary
3. Tableau filter types — overview
   3.1 Extract filters
   3.2 Data source filters
   3.3 Context filters
   3.4 Dimension filters (quick filters)
   3.5 Measure filters
   3.6 Date filters (discrete, continuous, relative)
   3.7 Filter actions and viz-in-tooltip filters
   3.8 Table calculation filters (late filters)
4. Tableau order of operations and where filters sit
5. Step by step: how to create each filter type
   5.1 Create an extract filter
   5.2 Create a data source filter
   5.3 Create a context filter
   5.4 Add a dimension quick filter and customize controls
   5.5 Add a measure filter and choose aggregation mode
   5.6 Create date filters: range and relative dates
   5.7 Build a filter action on a dashboard
   5.8 Use a table calc as a filter (late filtering)
6. Practical patterns, performance notes, and gotchas
   6.1 Cascading filters and dependent lists
   6.2 When to use context filters for performance vs when not to
   6.3 Extract vs data source filters: permanence and scope
   6.4 Relative dates and anchor points
   6.5 Table calc filters and order of operations implications
7. Examples and common tasks (recipes)
   7.1 Top N per group using context filters
   7.2 Dashboard drillthrough with filter actions
   7.3 Latest-date reporting using relative or latest-date filters
8. Reasoning summary (how this document was assembled)
9. Points that require verification or are uncertain

# 2. Purpose

This document translates the supplied tutorial transcript into an extended technical reference on Tableau filters. It explains what each filter type does, where it is applied in Tableau processing, exact steps to create them, and practical advice for performance and correct behavior.

Note on formatting and style: the structure and phrasing follow short clear sections with headings and bullets. See the uploaded guidelines for style constraints. 

# 3. Executive summary

* Tableau supports multiple filter types that execute in a strict order. Use extract and data source filters to reduce incoming rows. Use context filters when you need dependent filters or improved performance for large data sets. Dimension and measure filters provide interactive controls. Date filters include discrete, continuous, and relative modes. Filter actions and viz-in-tooltip provide interactive dashboard-driven filtering. Table calculation filters are applied after standard filters and are used for late filtering. Official Tableau documentation describes these concepts and the order of operations. ([Tableau Help][1])

# 4. Tableau filter types — overview

* Extract filters: limit what goes into a .hyper extract. They remove rows at extract creation or refresh. ([Tableau Help][2])
* Data source filters: applied at the data connection level to limit records returned to worksheets. ([Tableau Help][2])
* Context filters: create a primary subset that other filters are evaluated against. Context filters can change performance and enable dependent filtering. ([Tableau Help][3])
* Dimension filters (quick filters): discrete selections or wildcard/condition/top filters for categorical fields. ([Tableau Help][1])
* Measure filters: continuous or aggregated filtering options; can filter on raw values, aggregations, or standard deviations. ([Tableau Help][1])
* Date filters: discrete and continuous modes, plus relative dates and browse periods. Relative dates are anchored, usually to today, and can be changed. ([Tableau Help][4])
* Filter actions: dashboard-level interactions that let one view act as a filter for other views. ([Tableau Help][5])
* Table calc filters: filters built from table calculations. They are evaluated late, after most other filters, so they filter the post-calculation result. ([Tableau Help][6])

# 5. Tableau order of operations and where filters sit

* Key principle: Tableau applies filters according to its internal order of operations from top to bottom. The high level order begins with extract filters, then data source filters, then the latest date filter (if used), then context filters, then dimension and measure filters, then table calculation filters. Use this order to reason about which filters will limit data seen by other filters. ([Tableau Help][7])

* Practical implication: a filter placed earlier in the order removes rows from consideration for filters that execute later. For example, an extract filter removes rows before data reaches dimension filters. ([Tableau Help][2])

# 6. Step by step: how to create each filter type

Each subsection gives precise UI steps that match Tableau Desktop and web authoring menu items.

## 6.1 Create an extract filter

1. In Tableau Desktop, right click the data source in the Data pane and choose Extract Data.
2. In the Extract Data dialog, add field filters by clicking Add and select the field and values or conditions you want to include.
3. Optional: choose to aggregate data for visible dimensions or roll up dates to a particular grain.
4. Click Extract and save the .hyper extract. Note that extract filters are applied at extract creation and limit the rows in the resulting extract. To change them, regenerate the extract. ([Tableau Help][8])

Practical tip: keep a copy of the live data source or original file if you might need rows excluded by the extract later. ([Tableau Help][8])

## 6.2 Create a data source filter

1. Select the connection for your data source in the top-right of the Data Source page and click Filters.
2. Click Add, choose a field, and configure the filter (values, condition, or top N).
3. Apply. This filter limits records at the data source level but is not baked into an extract unless you use it when creating the extract. ([Tableau Help][2])

## 6.3 Create a context filter

1. Add a filter to the Filters shelf on a worksheet.
2. Open the filter pill menu and choose Add to Context. The pill turns gray and moves above non-context filters.
3. The result of the context filter becomes the subset used by subsequent non-context filters. Use this to compute top N per group or to improve speed when a single filter significantly reduces the data set. ([Tableau Help][3])

Performance note: context changes can require recomputing temporary results. Use only when needed and prefer a single selective context filter rather than many context filters. ([Tableau Help][3])

## 6.4 Add a dimension quick filter and customize controls

1. Right click a field on the view or in the Data pane and choose Show Filter.
2. Use the filter control dropdown to choose control type: single value list, single value dropdown, multiple values list, multiple values dropdown, slider, wildcard match, or custom lists.
3. Use the dropdown Customize menu to hide the All option, show an Apply button, or change Apply To Worksheets behavior. ([Tableau Help][1])

UX tip: enable Show Apply Button when selections cause expensive refreshes so users can make multiple choices before re-querying. ([Tableau Help][1])

## 6.5 Add a measure filter and choose aggregation mode

1. Drag a measure to the Filters shelf or right click a measure in the view and choose Filter.
2. Choose filter mode: All Values, Aggregated (for example Sum, Avg), or special modes such as standard deviation or attribute.
3. Configure the continuous range, or set At Least/At Most modes to restrict one boundary. ([Tableau Help][1])

Clarification: choosing All Values filters each raw row value; choosing Sum or another aggregation filters after grouping. This difference changes which values appear in the control and what records remain. ([Tableau Help][1])

## 6.6 Create date filters: range and relative dates

1. Drag the date field to the Filters shelf.
2. Choose discrete (Year, Quarter, Month) or continuous (Range of Dates, Relative Date).
3. For Relative Date, select the unit and period (for example last 3 months). The anchor defaults to Today but can be changed in the Edit Filter dialog. Browse Periods exposes quick choices like 1 day, 1 week, 1 month, 3 months, 1 year, and 5 years. ([Tableau Help][4])

## 6.7 Build a filter action on a dashboard

1. On a dashboard, select Dashboard > Actions.
2. Add a Filter action. Alternatively, use a view shortcut menu and choose Use as Filter to auto-create a filter action.
3. Configure source sheets, target sheets, and whether selection, hover, or menu triggers the action. Filter actions pass fields from the source to the target to filter target views. ([Tableau Help][5])

## 6.8 Use a table calc as a filter (late filtering)

1. Create the table calculation in the view (for example a moving average, rank, or percent of total).
2. Control-drag or copy the pill with the table calculation to the Filters shelf. The filter will evaluate after dimension and measure filters so it filters post-calculation results.
3. If the table calc is continuous, the filter control is a range; if discrete, the control follows discrete behaviors. ([Tableau Help][6])

Important: because table calc filters are late, they work against values after aggregation and other filters. This is necessary when you want to filter based on computed ranks or windowed aggregates.

# 7. Practical patterns, performance notes, and gotchas

## 7.1 Cascading filters and dependent lists

* Default behavior: filters are independent and combine via logical AND. Use the filter control dropdown and enable Only Relevant Values to make dropdown lists cascade and show only values relevant to current selections. This affects UX but does not change filter order. ([Tableau Help][1])

## 7.2 When to use context filters for performance

* Use context filters when a single filter can drastically reduce the data set and make subsequent queries faster. Create the context filter before adding other fields to shelves when possible. Recomputing context can be expensive when the data model or filters change. ([Tableau Help][3])

## 7.3 Extract vs data source filters: permanence and scope

* Extract filters determine what rows are included in the extract file. Data source filters limit data at the connection layer. If an extract is created after a data source filter is present, the extract may reflect that filter depending on workflow. Understand whether you want the exclusion permanent (extract) or adjustable in workbook sessions (data source filter). ([Tableau Help][8])

## 7.4 Relative dates and anchor points

* Relative date filters are dynamic relative to an anchor date. The default anchor is Today. You can change the anchor to support reproducible reports that use a fixed anchor date. Use browse periods for common quick selections. ([Tableau Help][4])

## 7.5 Table calc filters and order of operations implications

* Table calculation filters run late. If you need to filter based on a post-aggregation or window calculation, use a table-calc filter. Keep in mind that earlier filters still affect the input to the table calc. Use table calc filters only when necessary because they can complicate performance reasoning. ([Tableau Help][6])

# 8. Examples and common tasks (recipes)

## 8.1 Top N per group using context filters

* Goal: show top 10 states by sales within each region.
* Steps:

  1. Build view: State on rows, SUM(Sales) on columns.
  2. Add Region to Filters and choose the region values you want.
  3. Right click the Region filter pill and choose Add to Context. The pill becomes gray.
  4. On State, open filter, Top tab, By field, Top 10 by SUM(Sales). Because Region is a context, the top 10 calculation runs within the selected region, producing top N per region. ([Tableau Help][3])

## 8.2 Dashboard drillthrough with filter actions

* Goal: clicking a map point filters a line chart and a table on the same dashboard.
* Steps:

  1. Place map, line chart, and table onto a dashboard.
  2. Select the map, click Use as Filter or Dashboard > Actions > Add Action > Filter.
  3. Configure targets and clearing behavior. Now clicks or selections on the map pass values to the other views. ([Tableau Help][5])

## 8.3 Latest-date reporting using latest date filter

* Goal: always show most recent available date.
* Options: use a relative date filter set to Today or use the Latest Date filter option. The latest date filter runs after data source filters and before context filters according to Tableau order of operations. Verify anchor behavior for scheduled extracts or published workbooks. ([Tableau Help][7])

# 9. Reasoning summary

* I converted the supplied transcript into a structured technical document by extracting the distinct filter topics presented in the video, mapping each topic to Tableau help documentation for authoritative behavior, and then writing stepwise UI instructions for each filter type. The official Tableau help pages were used to confirm the order of operations, exact filter placement, and available options for relative dates, extract behavior, context filter behavior, and filter actions. Key sources include Tableau help pages for filtering, order of operations, extract behavior, and context filters. ([Tableau Help][7])

# 10. Points that require verification or are uncertain

* ASSUMPTION: The UI labels in the user’s Tableau version match the current Tableau Desktop labels used in the help docs. If the user runs a very old or very new release, menu text or dialog placement might differ. This may require verification against the specific Tableau version in use.
* ASSUMPTION: Server or cloud publishing behavior for latest-date or extract refreshes could differ based on Tableau Cloud scheduling and credentials. Confirm scheduling behavior after publishing.
* Verification needed: whether extract filters on complex logical table or multi-table models behave as pervasive or per-table in the user’s exact data model. Official docs note per-table vs pervasive behavior depending on logical table structure. Validate for your data model. ([Tableau Help][8])
* Verification needed: performance tradeoffs for context filters depend on data size, data source type, and whether Assume Referential Integrity is enabled. Confirm via testing on representative datasets. ([Tableau Help][3])

# 11. References (selected authoritative sources)

* Tableau Help: The Tableau Order of Operations. ([Tableau Help][7])
* Tableau Help: Filter Data from Your Views. ([Tableau Help][1])
* Tableau Help: Extract filters and extracting data. ([Tableau Help][8])
* Tableau Help: Use Context Filters. ([Tableau Help][3])
* Tableau Help: Filter Actions. ([Tableau Help][5])

[1]: https://help.tableau.com/current/pro/desktop/en-us/filtering.htm?utm_source=chatgpt.com "Filter Data from Your Views"
[2]: https://help.tableau.com/current/pro/desktop/en-us/filtering_datasource.htm?utm_source=chatgpt.com "Filter Data from Data Sources"
[3]: https://help.tableau.com/current/pro/desktop/en-us/filtering_context.htm?utm_source=chatgpt.com "Use Context Filters - Tableau Help"
[4]: https://help.tableau.com/current/pro/desktop/en-us/qs_relative_dates.htm?utm_source=chatgpt.com "Create Relative Date Filters"
[5]: https://help.tableau.com/current/pro/desktop/en-us/actions_filter.htm?utm_source=chatgpt.com "Filter Actions"
[6]: https://help.tableau.com/current/pro/desktop/en-us/calculations_calculatedfields_lod_filters.htm?utm_source=chatgpt.com "Filters and Level of Detail Expressions"
[7]: https://help.tableau.com/current/pro/desktop/en-us/order_of_operations.htm?utm_source=chatgpt.com "Tableau's Order of Operations"
[8]: https://help.tableau.com/current/pro/desktop/en-us/extracting_data.htm?utm_source=chatgpt.com "Extract Your Data"
