from usecases import utils


class Crowdsourcing:
    def __init__(self, path="data/crowdsourcing_final.csv"):
        self.crowd_data = utils.get_csv(path)

    def search(self, entity: str, relation: str) -> str:
        filtered_df = self.crowd_data[
            (self.crowd_data["Input1ID"] == f"wd:{entity}")
            & (self.crowd_data["Input2ID"] == f"wdt:{relation}")
        ]
        assert not filtered_df.empty, "No crowddata found"
        correct = filtered_df["CORRECT"].item()
        corrected = filtered_df["CORRECTED"].item()
        incorrect = filtered_df["INCORRECT"].item()
        result = filtered_df["Input3ID"].item()
        kappa = round(filtered_df["FleissKappa"].item(), 3)
        return correct, corrected, incorrect, result, kappa
    
    
