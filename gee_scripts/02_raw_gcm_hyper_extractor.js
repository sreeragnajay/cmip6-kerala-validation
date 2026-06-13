// ==============================================================================
// CMIP6 HISTORICAL HYPER-SPEED EXTRACTION PIPELINE (1990 - 2014)
// ==============================================================================

// 1. The exact 13 models needed for validation
var models = [
  'ACCESS-CM2', 'ACCESS-ESM1-5', 'BCC-CSM2-MR', 'CanESM5', 
  'EC-Earth3', 'EC-Earth3-Veg-LR', 'INM-CM4-8', 'INM-CM5-0', // Note: EC-Earth3-Veg-LR is corrected
  'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'NorESM2-LM', 'NorESM2-MM'
];

// 2. PASTE YOUR 77 POINTS HERE (Generated from Script 01)
var ptList = [
  // Example: [76.123, 9.456],
  // Paste array here...
];

// Convert list of coordinates to a Feature Collection of Points
var targetPoints = ee.FeatureCollection(ptList.map(function(p) { 
    return ee.Feature(ee.Geometry.Point(p)); 
}));

print("🚀 Generating extraction tasks for all 13 models...");

// 3. Loop through every model and generate a cloud extraction task
models.forEach(function(modelName) {

  // STRICTLY HISTORICAL: 1990-01-01 to 2014-12-31
  var modelCollection = ee.ImageCollection("NASA/GDDP-CMIP6")
    .filter(ee.Filter.eq('model', modelName))
    .filter(ee.Filter.eq('scenario', 'historical')) 
    .filterDate('1990-01-01', '2015-01-01') // End date is exclusive in GEE
    .select('pr'); 

  // THE HYPER-SPEED 'getRegion' C++ ENGINE (Bypasses geometry reduction)
  var rawTimeSeries = modelCollection.getRegion(targetPoints, 27830);

  // Format the raw array back into a clean Table
  var header = ee.List(rawTimeSeries.get(0));
  var data = rawTimeSeries.slice(1);

  var fastCollection = ee.FeatureCollection(data.map(function(row) {
    var dict = ee.Dictionary.fromLists(header, row);
    
    // Convert NASA flux (kg/m2/s) to standardized mm/day
    var precip_mm = ee.Number(dict.get('pr')).multiply(86400); 
    
    // Convert Earth Engine 'time' milliseconds to strict YYYY-MM-DD string
    var dateStr = ee.Date(ee.Number(dict.get('time'))).format('YYYY-MM-DD');
    
    return ee.Feature(null, {
      'date': dateStr,
      'latitude': dict.get('latitude'),
      'longitude': dict.get('longitude'),
      'precipitation_mm_day': precip_mm
    });
  }));

  // Purge any null values where models masked out ocean pixels
  var finalData = fastCollection.filter(ee.Filter.notNull(['precipitation_mm_day']));

  // 4. Send to Google Drive
  Export.table.toDrive({
    collection: finalData,
    description: modelName + '_Raw_GCM_1990_2014',
    folder: 'Raw_GCM_Thesis_Data',
    fileFormat: 'CSV',
    selectors: ['date', 'latitude', 'longitude', 'precipitation_mm_day']
  });
});

print("✅ Tasks generated! Go to the 'Tasks' tab on the right and click 'Run' on all 13.");
