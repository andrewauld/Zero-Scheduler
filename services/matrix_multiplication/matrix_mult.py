from flask import Flask, render_template
import os
import numpy as np

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../templates'))
app = Flask(__name__, template_folder=template_dir)

@app.route("/")
def main():
    return "Root is working. Check out /matrix_mult for the matrix multiplication service."

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))