# **COMPLETE NAVIGATION & FILTER PASSING SYSTEM - SUPERSTORE DATA**
**Step-by-Step Guide with Exact Clicks**

## **PART 1: CREATE 3 DASHBOARDS**

### **Step 1: Create Dashboard 1 - "Sales Overview"**
1.1. **Create new worksheet:**
- Click "New Worksheet" icon (bottom left)
- Rename: `Sales Summary`
- Drag `Category` to Rows
- Drag `Sales` to Columns
- Change Marks to "Bar"
- Drag `Profit` to Color
- Add filter: Right-click `Region` → "Show Filter"
<img width="1919" height="877" alt="image" src="https://github.com/user-attachments/assets/f60144c1-1259-4705-94ff-e4e8d35f7600" />

1.2. **Create dashboard:**
- Click "New Dashboard" icon
- Rename: `Sales Overview Dashboard`
- Drag `Sales Summary` sheet to dashboard
- Add title: Click "Show Dashboard Title" (left pane) → Edit to "Sales Overview"
<img width="1919" height="886" alt="image" src="https://github.com/user-attachments/assets/0187ce00-b677-4cb4-afd1-359781b18024" />

### **Step 2: Create Dashboard 2 - "Regional Analysis"**
2.1. **Create new worksheet:**
- New worksheet → Rename: `Regional Map`
- Double-click `State`
- Drag `Sales` to Color
- Drag `Profit` to Label
<img width="1919" height="876" alt="image" src="https://github.com/user-attachments/assets/ecd435b4-7e15-4dce-8a9b-6bac2bb19dc3" />

2.2. **Create dashboard:**
- New dashboard → Rename: `Regional Analysis Dashboard`
- Drag `Regional Map` sheet to dashboard
- Title: "Regional Analysis"
<img width="1919" height="886" alt="image" src="https://github.com/user-attachments/assets/0e546542-b057-4075-87fa-f7ef60123cd5" />

### **Step 3: Create Dashboard 3 - "Product Details"**
3.1. **Create new worksheet:**
- New worksheet → Rename: `Product Details`
- Drag `Sub-Category` to Rows
- Drag `Sales`, `Profit`, `Quantity` to Columns
- Change Marks to "Text"
<img width="1919" height="880" alt="image" src="https://github.com/user-attachments/assets/6c0beee6-070c-434e-8900-5919e8b08c33" />

3.2. **Create dashboard:**
- New dashboard → Rename: `Product Details Dashboard`
- Drag `Product Details` sheet to dashboard
- Title: "Product Details"

## **PART 2: CREATE GLOBAL FILTERS (Filter Passing)**

### **Step 4: Create Global Filter Parameter**
4.1. **Create Category Parameter:**
- Right-click in Data pane → "Create Calculated Field"
- Wait, cancel that
- Instead: Right-click anywhere in Data pane → "Create Parameter"
- Name: `Global Category`
- Data type: String
- Allowable values: **List**
- Click "Add from Field" → Select `Category`
- Current value: Select "(All)" if available, or first category
- Click "OK"

4.2. **Create Region Parameter:**
- Create another parameter
- Name: `Global Region`
- Data type: String
- Allowable values: List
- Add from Field: `Region`
- Current value: Select first item
- Click "OK"

### **Step 5: Create Calculated Fields for Filter Logic**
5.1. **Category Filter Logic:**
- Right-click in Data pane → "Create Calculated Field"
- Name: `Apply Category Filter`
- Formula:
```
[Global Category] = "(All)" OR [Category] = [Global Category]
```
- Click "OK"

5.2. **Region Filter Logic:**
- Create another calculated field
- Name: `Apply Region Filter`
- Formula:
```
[Global Region] = "(All)" OR [Region] = [Global Region]
```
- Click "OK"

### **Step 6: Apply Filters to All Worksheets**
6.1. **Apply to Sales Summary worksheet:**
- Go to `Sales Summary` worksheet
- Drag `Apply Category Filter` to Filters shelf
- Right-click the filter → "Filter"
- Check only "True"
- Click "OK"
- Repeat for `Apply Region Filter`

6.2. **Apply to Regional Map worksheet:**
- Go to `Regional Map` worksheet
- Drag both calculated fields to Filters shelf
- Set both to "True" only

6.3. **Apply to Product Details worksheet:**
- Go to `Product Details` worksheet
- Drag both calculated fields to Filters shelf
- Set both to "True" only

## **PART 3: ADD NAVIGATION BETWEEN DASHBOARDS**

### **Step 7: Create Navigation Menu on Each Dashboard**
7.1. **On Sales Overview Dashboard:**
- From left pane, drag "Horizontal Container" to top of dashboard
- Inside container, drag 3 "Text" objects
- Edit text boxes (double-click each):
  1. "🏠 Home"
  2. "📍 Regional"
  3. "📦 Products"

7.2. **Format navigation:**
- Select all 3 text boxes (Shift+click)
- Right-click → "Format"
- Set font size: 12pt
- Set font color: Blue
- Add separators: Edit middle text to "📍 Regional |"
- Edit last text to "📦 Products"

7.3. **Add navigation actions:**
- Right-click "📍 Regional" text → "Add Action" → "Go to Dashboard"
- Name: "Go to Regional Dashboard"
- Source: Check "Sheets" → Select this text object
- Target: Select "Regional Analysis Dashboard"
- Click "OK"

7.4. **Add to Products:**
- Right-click "📦 Products" text → "Add Action" → "Go to Dashboard"
- Configure same way to "Product Details Dashboard"
- Click "OK"

### **Step 8: Add Navigation to Regional Dashboard**
8.1. **Copy navigation menu:**
- Go back to Sales Overview Dashboard
- Select the entire horizontal container with navigation
- Ctrl+C to copy
- Go to Regional Analysis Dashboard
- Ctrl+V to paste

8.2. **Update actions:**
- Right-click "🏠 Home" → "Add Action" → "Go to Dashboard"
- Point to "Sales Overview Dashboard"
- Click "OK"
- Right-click "📦 Products" → Update action to point to Product Details Dashboard

8.3. **Add current page indicator:**
- Edit "📍 Regional" text → Change to "📍 Regional (Current)"
- Change color to dark gray (to indicate active page)

### **Step 9: Add Navigation to Products Dashboard**
9.1. **Paste navigation:**
- Copy from previous dashboard
- Paste on Product Details Dashboard

9.2. **Update actions:**
- Update "🏠 Home" to point to Sales Overview
- Update "📍 Regional" to point to Regional Analysis
- Mark current: "📦 Products (Current)"

## **PART 4: ENABLE FILTER PASSING BETWEEN DASHBOARDS**

### **Step 10: Add Parameter Controls to All Dashboards**
10.1. **On Sales Overview Dashboard:**
- Right-click `Global Category` parameter → "Show Parameter Control"
- Right-click `Global Region` parameter → "Show Parameter Control"
- Arrange them below navigation menu

10.2. **Format parameter controls:**
- Select both parameter controls
- Right-click → "Floating"
- Move to consistent location (e.g., top-right)
- Format to look like dropdowns

10.3. **Copy to other dashboards:**
- Select both parameter controls
- Ctrl+C
- Go to Regional Analysis Dashboard
- Ctrl+V (paste in same position)
- Repeat for Product Details Dashboard

### **Step 11: Test Filter Passing**
11.1. **Test scenario:**
- On Sales Overview Dashboard
- Change `Global Category` to "Technology"
- Change `Global Region` to "West"
- Click "📍 Regional" to navigate
- Verify Regional Map shows only West region, Technology category
- Click "📦 Products" to navigate
- Verify Product Details shows only West region, Technology products

## **PART 5: ADD RESET FILTERS BUTTON**

### **Step 12: Create Reset Mechanism**
12.1. **Create Reset Parameter:**
- Create new parameter
- Name: `Reset Trigger`
- Data type: String
- Allowable values: List
- Add values: "Reset All"
- Current value: Leave blank
- Display as: Slider
- Click "OK"

12.2. **Create Reset Calculated Field:**
- Right-click in Data pane → "Create Calculated Field"
- Name: `Reset Filters Logic`
- Formula:
```
[Reset Trigger]
```
- This is a dummy field that updates when parameter changes
- Click "OK"

### **Step 13: Add Reset Button to Each Dashboard**
13.1. **On Sales Overview Dashboard:**
- Add "Text" object to navigation container
- Edit text: "🔄 Reset All"
- Place at end of navigation menu

13.2. **Create Reset Action:**
- Right-click "🔄 Reset All" text → "Add Action" → "Change Parameter"
- Name: "Reset All Filters"
- Source: This text object (click "Select Sheeets" → choose the text)
- Target Parameter: `Reset Trigger`
- Value: "Reset All"
- Click "OK"

13.3. **Add second action to reset filters:**
- Right-click same text → "Add Action" → "Change Parameter"
- Name: "Reset Category"
- Target Parameter: `Global Category`
- Value: Enter `"(All)"` (with quotes)
- Click "OK"

13.4. **Add third action:**
- Right-click same text → "Add Action" → "Change Parameter"
- Name: "Reset Region"
- Target Parameter: `Global Region`
- Value: Enter `"(All)"`
- Click "OK"

### **Step 14: Add Auto-Reset Trigger**
14.1. **Create worksheet to trigger reset:**
- New worksheet → Rename: `Reset Helper` (hide this later)
- Drag `Reset Filters Logic` to Text on Marks card
- Add to each dashboard but make invisible

14.2. **Add to dashboards as hidden:**
- On each dashboard, add `Reset Helper` sheet
- Right-click its title → "Hide Title"
- Make it very small (1x1 pixel area)
- Place in corner

14.3. **Copy Reset Button to other dashboards:**
- Copy the "🔄 Reset All" text with all its actions
- Paste on Regional Analysis Dashboard
- Paste on Product Details Dashboard

## **PART 6: TEST COMPLETE SYSTEM**

### **Step 15: Comprehensive Testing**
15.1. **Test 1 - Navigation with Filters:**
- Start on Sales Overview
- Set Category = "Furniture", Region = "South"
- Click "📍 Regional" → Should see South region, Furniture only
- Click "📦 Products" → Should see Furniture products from South only

15.2. **Test 2 - Reset Functionality:**
- On any dashboard, click "🔄 Reset All"
- Check both filter parameters reset to "(All)"
- Verify all data shows (no filters applied)

15.3. **Test 3 - Bidirectional Filter Passing:**
- From Products dashboard, set new filters
- Navigate to Regional dashboard → Filters should persist
- Navigate to Sales Overview → Filters should persist

### **Step 16: Enhance Navigation**
16.1. **Add breadcrumb trail:**
- On each dashboard, add text showing current filters
- Create calculated field: `Current Filter Display`
- Formula:
```
"Viewing: " + 
IF [Global Category] = "(All)" THEN "All Categories" ELSE [Global Category] END +
" | " +
IF [Global Region] = "(All)" THEN "All Regions" ELSE [Global Region] END
```
- Add this as text object below navigation

16.2. **Add back button:**
- Add "◀ Back" text in navigation
- Use "Go to Dashboard" action pointing to previous dashboard
- Requires tracking previous page (more complex)

## **PART 7: PUBLISH AND FINALIZE**

### **Step 17: Publish to Tableau Public**
17.1. **Final checks:**
- Save workbook locally first: Ctrl+S
- Name: "Superstore_Navigation_System"

17.2. **Test all interactions:**
- Navigation between all 3 dashboards ✓
- Filter persistence during navigation ✓
- Reset button works on all dashboards ✓
- Filters apply correctly to all views ✓

17.3. **Publish:**
- Click "Server" menu → "Tableau Public" → "Save to Tableau Public"
- Login with your Tableau Public account
- Publish as: "Superstore Navigation System"
- Share the URL

### **Step 18: Create User Guide (Optional but Helpful)**
18.1. **Add instructions dashboard:**
- Create one more dashboard: "Instructions"
- Add text explaining:
  1. Use navigation buttons at top
  2. Use filters at top-right
  3. Click reset button to clear all
  4. Filters persist when navigating

18.2. **Make it the home page:**
- Update "🏠 Home" navigation to point to Instructions dashboard
- Or make Sales Overview the default home

## **TROUBLESHOOTING SPECIFIC ISSUES**

### **Filters Not Passing:**
1. Check parameter names match exactly
2. Verify calculated fields use same parameter names
3. Ensure filters are set to "True" only on worksheets

### **Reset Button Not Working:**
1. Check parameter values have quotes: `"(All)"`
2. Verify all three change parameter actions are attached
3. Test each parameter resets individually

### **Navigation Links Broken:**
1. Check dashboard names match exactly
2. Verify "Go to Dashboard" actions point to correct targets
3. Test after publishing (some features work better published)

### **Performance Issues:**
1. Use extracts instead of live connections
2. Hide unused fields from data pane
3. Use fewer marks on maps for better performance

## **QUICK REFERENCE - EXACT STEPS FOR ANY DATASET**

1. **Create 3 parameters** (Global filters)
2. **Create 2 calculated fields** (Filter logic)
3. **Apply to all worksheets** (Drag to filters, set to True)
4. **Add parameter controls** to all dashboards
5. **Create navigation menu** (Text objects with Go to Dashboard actions)
6. **Add reset button** (Text object with 3 Change Parameter actions)
7. **Test thoroughly** before publishing

This system now gives you full navigation between dashboards with persistent filters and a reset button - exactly as requested!
