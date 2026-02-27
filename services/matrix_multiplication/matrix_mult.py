from flask import Flask
import os
import numpy as np

app = Flask(__name__)

@app.route("/")
def main():
    return "At least the root is working..."

@app.route("/matrix_mult")
def matrix_mult():

    # Creating square matrices of dimensions 10k x 10k -> 15k x 15k
    matrixDimensions = np.random.randint(10000, 15000)

    matrixA = np.random.rand(matrixDimensions, matrixDimensions)
    matrixB = np.random.rand(matrixDimensions, matrixDimensions)

    # Multiply the matrices to stress test the system
    with np.errstate(divide='ignore', over='ignore', invalid='ignore'):
        result = np.matmul(matrixA, matrixB)
    return str(result)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 8080)))