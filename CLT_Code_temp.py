







##calculations for gasoline
results_bCLT_energy[3][61] = CLT_building_materials_const_energy_impacts[4][2] * construction_impacts_CLT_building[1][4]
results_bCLT_energy[4][61] = CLT_building_materials_const_energy_impacts[4][2] * construction_impacts_CLT_building[2][4]
results_bCLT_energy[5][61] = CLT_building_materials_const_energy_impacts[4][2] * construction_impacts_CLT_building[3][4]
results_bCLT_energy[6][61] = CLT_building_materials_const_energy_impacts[4][2] * construction_impacts_CLT_building[4][4]
results_bCLT_energy[7][61] = CLT_building_materials_const_energy_impacts[4][2] * construction_impacts_CLT_building[5][4]
results_bCLT_energy[8][61] = CLT_building_materials_const_energy_impacts[4][2] * construction_impacts_CLT_building[6][4]

##calculations for electricity-- add
results_bCLT_energy[3][62] = 0
results_bCLT_energy[4][62] = 0
results_bCLT_energy[5][62] = 0
results_bCLT_energy[6][62] = 0
results_bCLT_energy[7][62] = 0
results_bCLT_energy[8][62] = 0

### sum energy totals for diesel, gasoline and electricity ##this most probably will not work so find another method-- probably to slice and then sum
CLT_building_materials_const_energy_impacts[0][4] = "Total"
CLT_building_materials_const_energy_impacts[5][4] = CLT_building_materials_const_energy_impacts["Non renewable, fossil"].sum()
CLT_building_materials_const_energy_impacts[6][4] = CLT_building_materials_const_energy_impacts["Non-renewable, nuclear"].sum()
CLT_building_materials_const_energy_impacts[7][4] = CLT_building_materials_const_energy_impacts["Non-renewable, biomass"].sum()
CLT_building_materials_const_energy_impacts[8][4] = CLT_building_materials_const_energy_impacts["Renewable, wind, solar, geothe"].sum()
CLT_building_materials_const_energy_impacts[9][4] = CLT_building_materials_const_energy_impacts["Renewable, biomass"].sum()
CLT_building_materials_const_energy_impacts[10][4] = CLT_building_materials_const_energy_impacts["Renewable, water"].sum()

#energy_impacts_CLT_building[1][1] = energy_impacts_CLT[1].sum() +