import pandas as pd
import geopandas as gpd

print("Iniciando o script...")
print("Carregando arquivos...")

fp_municipios = "dados_originais/BR_Municipios_2022.shp"
fp_biomas = "dados_originais/Biomas_250mil/lm_bioma_250.shp" 
fp_focos = "dados_originais/focos_mensal_br_202508.csv" 

gdf_municipios = gpd.read_file(fp_municipios)
gdf_biomas = gpd.read_file(fp_biomas)
df_focos = pd.read_csv(fp_focos)

#print("Colunas Biomas:")
#print(gdf_biomas.columns) - depurar

print("Arquivos carregados com sucesso.")
print("\nPreparando os dados...")
gdf_focos = gpd.GeoDataFrame(
    df_focos,
    geometry=gpd.points_from_xy(df_focos.lon, df_focos.lat),
    crs="EPSG:4326"
)
gdf_focos = gdf_focos.to_crs(gdf_municipios.crs)
gdf_biomas = gdf_biomas.to_crs(gdf_municipios.crs)
gdf_amazonia = gdf_biomas[gdf_biomas['Bioma'] == 'Amazônia']

print("\nIniciando análise espacial...")
focos_na_amazonia = gpd.sjoin(gdf_focos, gdf_amazonia, how="inner", predicate="intersects")
focos_na_amazonia = focos_na_amazonia.drop(columns='index_right')
focos_com_municipio = gpd.sjoin(focos_na_amazonia, gdf_municipios, how="inner", predicate="intersects")
contagem_focos = focos_com_municipio.groupby('NM_MUN').size().reset_index(name='t_focos')
print("Análise concluída. Top 5 municípios:")
print(contagem_focos.sort_values(by='t_focos', ascending=False).head())

print("\nExportando o resultado...")
municipios_com_focos = gdf_municipios.merge(contagem_focos, on='NM_MUN', how='left')
municipios_com_focos['t_focos'] = municipios_com_focos['t_focos'].fillna(0)
municipios_com_focos['t_focos'] = municipios_com_focos['t_focos'].astype(int)

# Filtra apenas os municípios que tiveram focos e ordena do maior para o menor
resultado_csv = municipios_com_focos[municipios_com_focos['t_focos'] > 0].sort_values(by='t_focos', ascending=False)
resultado_csv.to_csv('dados_processados/resultado_contagem_focos.csv', index=False, sep=';', encoding='utf-8-sig')
fp_saida = "dados_processados/municipios_amazonia_focos.shp"
municipios_com_focos.to_file(fp_saida, driver='ESRI Shapefile', encoding='utf-8')

print(f"\nConcluido! O resultado foi salvo em: {fp_saida}")
