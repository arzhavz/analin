from core.technical import StockAnalyzer
from core.fundamental import get_fundamental_data
from report.printer import print_analysis
from visual.plotter import plot_technical_chart

if __name__ == "__main__":
    ticker = "ITMG.JK" #input("Enter stock ticker (e.g., AAPL, BBCA.JK): ")
    result, df = StockAnalyzer(ticker).analyze_all()

    if "error" not in result:
        fundamental = get_fundamental_data(ticker)
        result["Fundamental"] = fundamental

        print_analysis(result)
        plot_technical_chart(df, ticker)
    else:
        print(result["error"])
