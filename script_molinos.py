import pandas as pd
import numpy as np
from tensorflow.keras import model
import sys
from sklearn.metrics import mean_squared_error

linkAModelo = "https://github.com/Nacho2904/CURSO-LEARNING1/blob/tareas/modelo_molinos.h5"

def eliminarFilasConPotenciasNegativas(dfMolinos: pd.DataFrame) -> pd.DataFrame:
	
	dfMolinosFiltered = dfMolinos.copy()
	
	for column in dfMolinos.columns[::-1]:
  		dfMolinosFiltered = dfMolinosFiltered[dfMolinosFiltered[column] > 0]

	return dfMolinosFiltered

def transformarVelocidadACoordenadasCartesianas(dfMolinos: pd.DataFrame) -> pd.DataFrame:

	dfMolinosCartesianas = dfMolinos.copy()
	
	dfMolinosCartesianas["Direction"] = dfMolinos["Direction"] - 90
	dfMolinosCartesianas["Vx"] = dfMolinos["Velocity"]*np.cos(dfMolinos["Direction"])
	dfMolinosCartesianas["Vy"] = -dfMolinos["Velocity"]*np.sin(dfMolinos["Direction"])
	dfMolinosCartesianas = dfMolinosCartesianas.drop(columns = ["Direction", "Velocity"])

	return dfMolinosCartesianas

def extraerFeaturesYTargetsDeLosDatos(dfMolinos: pd.DataFrame) -> pd.DataFrame:
	#devuelve una matriz con las potencias y una segunda matriz con las velocidades como targets

	datosComoMatriz = np.array(dfMolinos)
	np.random.shuffle(datosComoMatriz)

	return datosComoMatriz[:int(datosComoMatriz.shape[0]),:-2], datosComoMatriz[:int(datosComoMatriz.shape[0]),-2:]

def main():

	pathAArchivoConDatos = sys.argv[1]
	dfMolinos = pd.read_csv(pathAArchivoConDatos)
	dfMolinosProcesado = transformarVelocidadACoordenadasCartesianas(eliminarFilasConPotenciasNegativas(dfMolinos))
	inputs, targets = extraerFeaturesYTargetsDeLosDatos(dfMolinosProcesado)
	modelo = model.load("modelo_molinos.h5")
	predicciones = modelo.predict(inputs)
	print(mean_squared_error(predicciones, targets))

main()
