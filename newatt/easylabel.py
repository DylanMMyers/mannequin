import opencv2

def main():
    app = QApplication(sys.argv)
    window = IntegratedMeasurementTool()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()