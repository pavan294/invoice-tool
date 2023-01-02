
import { addDefaultTags, TradingStages } from '@trading/cdk-patterns';
import { App } from 'aws-cdk-lib';
import 'source-map-support/register';
import { AwsAccount, AwsContext, AwsRegion } from '../lib/enums';
import { S3Stack } from '../lib/s3-stack-stack';

    
const props = {
    "dev": { 
        stage: TradingStages.Dev, 
        context: AwsContext.Dev, 
        env: { account: AwsAccount.Dev, region: AwsRegion.Dev }},
    "prod": { stage: TradingStages.Prod, 
        context: AwsContext.Prod, 
        env: { account: AwsAccount.Prod, region: AwsRegion.Prod }},
};
const stackDescription: string = "Nordpool Invoice Downloader app-specific S3 resources";

const app = new App();

//deploy to Stage DEV
const s3StackDev = new S3Stack(app, `${props.dev.stage}-${props.dev.context}-nordpool-invoice-downloader-s3`,{
    env: props.dev.env,
    context: props.dev.context,
    stage: props.dev.stage,
    description: stackDescription
});

addDefaultTags(s3StackDev, props.dev.stage, props.dev.context);


//deploy to Stage PROD
const s3StackProd = new S3Stack(app, `${props.prod.stage}-${props.prod.context}-nordpool-invoice-downloader-s3`,{
  env: props.prod.env,
  context: props.prod.context,
  stage: props.prod.stage,
  description: stackDescription
});

addDefaultTags(s3StackProd, props.prod.stage, props.prod.context);

