import pytorch_lightning as pl
import torch
from torch import nn
import pandas as pd
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler
import mlflow
import mltable

class StockPriceModel(pl.LightningModule):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=64, num_layers=2, batch_first=True)
        self.linear = nn.Linear(64, 1)

    def forward(self, x):
        x, _ = self.lstm(x)
        return self.linear(x[:, -1])

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = nn.MSELoss()(y_hat, y)
        self.log('train_loss', loss)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=0.001)

def prepare_data(data_path):
    tbl = mltable.load(data_path)
    df = tbl.to_pandas_dataframe()
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df['Close'].values.reshape(-1, 1))
    
    sequences = []
    targets = []
    for i in range(len(scaled_data) - 30):
        sequences.append(scaled_data[i:i+30])
        targets.append(scaled_data[i+30])
    
    return torch.FloatTensor(sequences), torch.FloatTensor(targets)

if __name__ == "__main__":
    mlflow.pytorch.autolog()
    data_path = os.environ.get("input_data")
    X, y = prepare_data(data_path)
    
    dataset = TensorDataset(X, y)
    train_loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    model = StockPriceModel()
    trainer = pl.Trainer(max_epochs=50)
    trainer.fit(model, train_loader)

    mlflow.pytorch.log_model(model, "model")
