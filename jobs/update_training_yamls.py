import yaml
from datetime import datetime

def update_train_yaml():
    with open('train.yml', 'r') as file:
        train_yaml = yaml.safe_load(file)
    
    # Update the job name with current date
    current_date = datetime.now().strftime('%Y%m%d')
    train_yaml['name'] = f"masb-jk-run-{current_date}"
    
    # Update any other fields as necessary
    # For example:
    # train_yaml['inputs']['data']['path'] = f"azureml:MASB_JK@{current_date}"
    
    with open('train.yml', 'w') as file:
        yaml.dump(train_yaml, file, default_flow_style=False)

def update_deploy_yaml():
    with open('deploy.yml', 'r') as file:
        deploy_yaml = yaml.safe_load(file)
    
    # Update the model version or any other fields
    # For example:
    # deploy_yaml['model'] = f"azureml:MASB_JK_model:{current_date}"
    
    with open('deploy.yml', 'w') as file:
        yaml.dump(deploy_yaml, file, default_flow_style=False)

if __name__ == "__main__":
    update_train_yaml()
    update_deploy_yaml()
    print("Training and deployment YAML files updated successfully.")
