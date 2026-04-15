# 1. Introduction

A radar chart compares several variables by arranging them around a circle and showing their values as distances from a central point. Tableau does not include this chart type by default. You build it manually using calculations that convert values into coordinates.

This tutorial assumes zero prior knowledge of Tableau. Each click and field creation is spelled out clearly.

# 2. Understanding the Radar Chart Structure

## 2.1 What the chart contains

* A **center point** where all axes meet.
* Several **axes** arranged around a circle.
* A **grid background** shaped like a spider web.
* A **polygon** that connects the values along each axis.
* **Dots** on each axis to show values.
* **Labels** identifying those values.

## 2.2 Why we need calculations

Radar charts rely on converting polar coordinates (angle + radius) into classic x and y coordinates. Tableau can place points on a graph only when we supply x and y.

The transcript discusses circle equations and trigonometry, which are the basis for those conversions. 

# 3. Setting Up the Workbook

## 3.1 Open Tableau

1. Launch Tableau Desktop.
2. On the start page, look for “Sample Workbooks”.
3. Choose “Sample Superstore”.
4. Tableau loads a dataset automatically.

You are now on a blank sheet.

## 3.2 Create a new worksheet

1. At the bottom left, select the icon that looks like a small chart.
2. A new empty sheet opens.

# 4. Create All Required Calculated Fields

You will create five separate calculations. Each one is essential.

## 4.1 Calculated Field: Month

Purpose: Extract month names from the date field.

Steps

1. Go to the left **Data pane**.
2. Right-click anywhere in that pane.
3. Choose **Create Calculated Field**.
4. Name the new field: **Month**.
5. In the editor, type:

```
DATENAME('month', [Order Date])
```

6. Click OK.

Verification
Drag **Month** onto Rows. You should see January through December listed.
If you see multiple duplicate month names, right-click Month → Convert to Discrete.

## 4.2 Calculated Field: Angle

Purpose: Assign a rotational angle for each month.

Steps

1. Right-click the Data pane → Create Calculated Field.
2. Name it **Angle**.
3. Enter:

```
RUNNING_SUM(1) * (2 * PI() / 12)
```

4. Click OK.

At this stage, the angle is a simple sequence of 12 equal slices of a circle.

## 4.3 Calculated Field: Distance

Purpose: The distance from the center for each point.

Steps

1. Right-click → Create Calculated Field.
2. Name it **Distance**.
3. Enter:

```
SUM([Sales])
```

4. Click OK.

This tells Tableau that our “radius” is simply the total sales for each month.

## 4.4 Calculated Field: X-Axis

1. Right-click → Create Calculated Field.
2. Name it **X Axis**.
3. Enter:

```
[Distance] * COS([Angle])
```

4. Click OK.

## 4.5 Calculated Field: Y-Axis

1. Create another calculation.
2. Name it **Y Axis**.
3. Enter:

```
[Distance] * SIN([Angle])
```

4. Click OK.

These two fields are the actual coordinates that Tableau will plot.

# 5. Build the Base Radar Shape

## 5.1 Place the fields

1. Drag **Month** onto the **Marks card → Detail**.
2. Drag **Angle** onto **Detail**.
3. Click the small drop-down on Angle → **Edit Table Calculation**.
4. In “Compute Using”, select **Month** so the running sum uses month order.

## 5.2 Draw the points using coordinates

1. Drag **X Axis** to **Columns**.
2. Drag **Y Axis** to **Rows**.

You will see a rough circular scatterplot.

## 5.3 Convert the scatterplot into a polygon

1. On the Marks card, change type from **Automatic** to **Polygon**.
2. Drag **Angle** to **Path** so Tableau knows the order in which to connect points.

You should now see a closed shape.

# 6. Add Multiple Years as Series

## 6.1 Color coding

1. Drag **Order Date** (Year) onto **Color**.
2. Reduce opacity on the Marks card so multiple polygons can overlap cleanly.

# 7. Correct the Rotation and Direction

The transcript explains that the months appear reversed at first. 

## 7.1 Reverse the month direction

Edit the **Angle** calculation:

```
- RUNNING_SUM(1) * (2 * PI() / 12)
```

The shape flips.

## 7.2 Rotate the whole chart by ninety degrees

Adjust the same calculation:

```
- RUNNING_SUM(1) * (2 * PI() / 12) + PI() / 2
```

If the background later does not align, you may adjust this rotation slightly.

# 8. Create a Perfect Circle by Fixing the Axes

The transcript uses the range −120000 to +120000 because monthly sales fall inside that range. 

## 8.1 Edit the X-Axis

1. Right-click the bottom axis → **Edit Axis**.
2. Choose **Fixed**.
3. Set:

   * Minimum: -120000
   * Maximum: 120000
4. Click OK.

## 8.2 Edit the Y-Axis

Repeat the same settings.

Now the shape becomes uniformly round.

# 9. Add the Spider-Web Background Image

## 9.1 Open background image settings

1. Go to the top menu → **Map**.
2. Choose **Background Images**.
3. Select **Sample Superstore**.

## 9.2 Add your image

1. Click **Add Image**.
2. Browse to your spider-web graphic.
3. Set the X Range:

   * -120000 to 120000
4. Set the Y Range:

   * -120000 to 120000
5. Press Enter after typing each value.
6. Click OK.

## 9.3 Realign using rotation if needed

If the “December” spoke is not on top of the background’s December axis, adjust the rotation inside the Angle formula.

The transcript experiments with values such as:

```
- RUNNING_SUM(1) * (2 * PI() / 12) + PI() * 2.4
```

Try adjustments until visually aligned. 

# 10. Add Dots at Each Month (Dual Axis)

## 10.1 Duplicate the Y-Axis

1. Hold Ctrl (or Option on Mac).
2. Drag **Y Axis** from Rows onto Rows again.
3. Tableau now shows two sets of marks.

## 10.2 Change the mark type for the second axis

1. Click the second Marks card.
2. Change type from Polygon to **Shape**.
3. Pick the circle shape.
4. Increase size slightly.

## 10.3 Blend both axes

1. Right-click on the second axis → **Dual Axis**.
2. Right-click again → **Synchronize Axis**.
3. Right-click both axes → **Hide Header**.

# 11. Add Labels to the Dots

## 11.1 Place labels

1. On the Marks card (the “circle” version), drag **Sales** to **Label**.
2. Click Label → Format:

   * Zero decimals
   * Units: Thousands
   * Currency symbol: Enabled

The transcript displays similar formatting. 

# 12. Clean the Tooltip

## 12.1 Remove clutter

1. On the Marks card (polygon and circle), click **Tooltip**.
2. Delete fields you do not want.
3. Keep only Month, Year, and Sales.

This matches the simplified tooltip described.

# 13. Lock the Layout

## 13.1 Turn off zoom and pan

1. Go to **Map**.
2. Uncheck **Allow Pan and Zoom**.

This prevents accidental distortion of the spider background.

# 14. Add a Year Filter

## 14.1 Enable selection

1. Drag **Order Date** (Year) into Filters.
2. Right-click it → **Show Filter**.
3. Change filter type to **Dropdown**.

You can toggle years on and off.

# 15. What You Should Now See

The final worksheet contains:

* A polygon radar chart for each selected year.
* Dots for each month.
* A spider-web background aligned to the spokes.
* Clean labels and tooltips.
* A controllable filter for years.

Everything described here follows the sequence and logic in the transcript. 

If you want next steps, you could expand this into a dashboard layout with titles, dynamic legends, or a parameter that switches metrics from Sales to Profit.
