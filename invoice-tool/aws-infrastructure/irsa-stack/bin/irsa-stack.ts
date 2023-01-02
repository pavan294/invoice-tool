
import { addDefaultTags, TradingStages } from '@trading/cdk-patterns';
import { App } from 'aws-cdk-lib';
import 'source-map-support/register';
import { AwsAccount, AwsContext, AwsRegion, K8sNamespace, K8sServiceAccountApi, K8sServiceAccountCronJob } from '../lib/enums';
import { AwsIrsaAppAssetsStack } from '../lib/irsa-stack';
    
const props = {
    "dev": { 
        stage: TradingStages.Dev, 
        context: AwsContext.Dev, 
        env: { account: AwsAccount.Dev, region: AwsRegion.Dev },
        k8sNamespace: K8sNamespace.Dev},
    "prod": { stage: TradingStages.Prod, 
        context: AwsContext.Prod, 
        env: { account: AwsAccount.Prod, region: AwsRegion.Prod },
        k8sNamespace: K8sNamespace.Prod },
};
const stackDescription: string = "Nordpool Invoice Downloader app-specific IRSA resources";

const app = new App();

//deploy to Stage DEV
const awsIrsaIamAssetsApiStackDev = new AwsIrsaAppAssetsStack(app, `${props.dev.stage}-${props.dev.context}-nordpool-invoice-downloader-api-irsa`,{
    env: props.dev.env,
    context: props.dev.context,
    stage: props.dev.stage,
    k8sNamespace: props.dev.k8sNamespace,
    k8sServiceAccount: K8sServiceAccountApi.Dev,
    description: stackDescription
});

addDefaultTags(awsIrsaIamAssetsApiStackDev, props.dev.stage, props.dev.context);

const awsIrsaIamAssetsCronJobStackDev = new AwsIrsaAppAssetsStack(app, `${props.dev.stage}-${props.dev.context}-nordpool-invoice-downloader-cronjob-irsa`,{
  env: props.dev.env,
  context: props.dev.context,
  stage: props.dev.stage,
  k8sNamespace: props.dev.k8sNamespace,
  k8sServiceAccount: K8sServiceAccountCronJob.Dev,
  description: stackDescription
});

addDefaultTags(awsIrsaIamAssetsCronJobStackDev, props.dev.stage, props.dev.context);

//deploy to Stage PROD
const awsIrsaIamAssetsApiStackProd = new AwsIrsaAppAssetsStack(app, `${props.prod.stage}-${props.prod.context}-nordpool-invoice-downloader-api-irsa`,{
    env: props.prod.env,
    context: props.prod.context,
    stage: TradingStages.Prod,
    k8sNamespace: props.prod.k8sNamespace,
    k8sServiceAccount: K8sServiceAccountApi.Prod,
    description: stackDescription
});

addDefaultTags(awsIrsaIamAssetsApiStackProd, props.prod.stage, props.prod.context);

const awsIrsaIamAssetsCronJobStackProd = new AwsIrsaAppAssetsStack(app, `${props.prod.stage}-${props.prod.context}-nordpool-invoice-downloader-cronjob-irsa`,{
  env: props.prod.env,
  context: props.prod.context,
  stage: TradingStages.Prod,
  k8sNamespace: props.prod.k8sNamespace,
  k8sServiceAccount: K8sServiceAccountCronJob.Prod,
  description: stackDescription
});

addDefaultTags(awsIrsaIamAssetsCronJobStackProd, props.prod.stage, props.prod.context);
