# Creating an Interactive Toggle Switch in Tableau

A comprehensive guide to building a metric toggle that's more intuitive than standard filters, with responsive colors that double as a legend.

---

## Why Use a Toggle Switch?

Traditional single-value filters work, but toggle switches provide:
- **Better UX**: More intuitive than dropdown filters
- **Visual feedback**: Colors indicate selected state
- **Built-in legend**: No separate legend needed
- **Cleaner design**: More polished, professional appearance

---

## Step 1: Create the Parameter

**Purpose**: Store the currently selected metric

1. Create a new parameter (right-click in Data pane → Create Parameter)
2. Configure:
   - **Name**: `Toggle Param`
   - **Data type**: String
   - **Current value**: Leave empty (blank)
3. Right-click the parameter → **Show Parameter**

---

## Step 2: Create Calculated Fields

You need two calculated fields for the toggle logic.

### Field 1: Toggle - Select

**Purpose**: Identifies which metric is currently selected

```tableau
IF [Toggle Param] = [Pivot Field Names]
THEN TRUE
ELSE FALSE
END
```

**What it does**: Returns TRUE for the selected metric, FALSE otherwise

> **Note**: `Pivot Field Names` is like Measure Names but works in calculated fields. See separate tutorials for measure names/values in calculations.

### Field 2: Toggle - Name for Param

**Purpose**: Shows the *opposite* metric name (the one you can switch TO)

```tableau
IF [Toggle Param] = "Price"
THEN "Volume"
ELSE "Price"
END
```

**Logic**: 
- If Price is selected → show "Volume" (what you can switch to)
- If Volume is selected → show "Price" (what you can switch to)

---

## Step 3: Build the Toggle Structure

1. Create a new worksheet (name it "Toggle Switch")
2. Drag `Toggle - Name for Param` to the Marks card
3. Change mark type from Automatic → **Shape**
4. Set `Toggle - Name for Param` to determine the **Shape**

---

## Step 4: Add Toggle to Dashboard

1. Create/open your dashboard
2. Add the "Toggle Switch" worksheet
3. **Hide the title**
4. Set to **Entire View**

---

## Step 5: Add Parameter Action (The "Click" Functionality)

**Purpose**: Make the toggle actually switch when clicked

1. Dashboard menu → **Actions** → **Add Action** → **Change Parameter**
2. Configure:
   - **Source Sheets**: Check only "Toggle Switch"
   - **Target Parameter**: `Toggle Param`
   - **Source Field**: `Toggle - Name for Param`
3. Click OK

**Test it**: Click the toggle—it should switch between circle and square shapes

---

## Step 6: Customize the Toggle Shapes

Default circles/squares aren't intuitive. Let's use custom toggle graphics.

1. Go back to "Toggle Switch" worksheet
2. Click on the Shape legend → **Edit Shapes**
3. Choose a shape palette (e.g., "Filter Images")
4. **Important**: Assign shapes *opposite* to what they represent:
   - **When Volume is showing** (parameter = Volume) → assign the **BLUE toggle** (for Price)
   - Click toggle to switch
   - **When Price is showing** (parameter = Price) → assign the **GREEN toggle** (for Volume)

**Why opposite?**: The parameter stores what's selected, but the shape shows what you can switch TO.

> **Note**: See separate tutorial for loading custom shapes into Tableau

---

## Step 7: Connect Toggle to Your Chart

1. Go to your chart worksheet
2. Remove any existing metric filters
3. Drag `Toggle - Select` to Filters
4. Select only **TRUE**

**Test it**: Toggle should now control which metric displays in your chart

---

## Step 8: Resize and Clean Up Toggle

1. Return to "Toggle Switch" worksheet
2. Use **Size slider** in Marks → increase size
3. Click **Tooltip** → delete all content (prevents showing opposite metric name)

---

## Step 9: Create Responsive Labels

**Goal**: Labels change color based on selected state

### Create the Label Worksheet

1. New worksheet (name it "Switch Labels")
2. Drag `Pivot Field Names` → Columns
3. Drag `Pivot Field Names` → Marks card **twice**:
   - One instance: Change to **Label**
   - One instance: Change to **Color**
4. Drag `Toggle - Select` → Marks card
5. Change to **Color**

### Configure Label Colors - First State (Volume Selected)

1. Click toggle so Volume is selected
2. Edit Colors for the `Toggle - Select` legend:
   - **False** (not selected) → Black
   - **True** (selected) → Green (matches Volume in chart)

### Configure Label Colors - Second State (Price Selected)

1. Click toggle to switch to Price
2. Edit Colors again:
   - **False** → Black
   - **True** → Blue (matches Price in chart)

---

## Step 10: Format the Labels

1. **Hide title**
2. Right-click header → **Uncheck "Show Header"**
3. Format worksheet:
   - **Font**: Increase size, darken color
   - **Alignment** → Horizontal: **Center**
   - **Shading** → Worksheet: **None**
   - **Borders** → Row Divider: **None**

---

## Step 11: Assemble on Dashboard

1. Add "Switch Labels" worksheet to dashboard
2. Set to **Entire View**
3. Resize so toggle sits **between** the labels
4. Layout tab → Move "Toggle Switch" **in front of** "Switch Labels"
5. Right-click Toggle Switch → Format → Shading: **None** (transparent background)

---

## Final Result

You now have:
- ✅ Toggle switches between metrics on click
- ✅ Toggle color matches selected metric
- ✅ Label color highlights selected metric
- ✅ Opposite label stays black (unselected state)
- ✅ Chart updates based on toggle selection
- ✅ No separate legend needed—toggle IS the legend

---

## Key Concepts Recap

| Component | Purpose |
|-----------|---------|
| `Toggle Param` | Stores currently selected metric |
| `Toggle - Select` | Returns TRUE/FALSE for filtering |
| `Toggle - Name for Param` | Shows opposite metric (for switching) |
| Parameter Action | Enables click-to-switch functionality |
| Responsive colors | Provides visual feedback of state |

---

## Troubleshooting

**Toggle not switching?**
- Verify parameter action targets correct parameter
- Check source field is `Toggle - Name for Param`

**Colors not updating?**
- Ensure `Toggle - Select` is on Marks as Color
- Re-edit color legends after each toggle state

**Chart not filtering?**
- Confirm `Toggle - Select` filter is set to TRUE only
- Check parameter is properly linked to chart logic
