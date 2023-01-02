
import { IrsaRole, TradingStages } from '@trading/cdk-patterns';
import { Stack, StackProps } from 'aws-cdk-lib';
import { ManagedPolicy } from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import { K8sNamespace, K8sServiceAccountApi, K8sServiceAccountCronJob } from './enums';

export interface AwsIrsaAppAssetsStackProperties extends StackProps {
  
  /**
   * Relates resources to ownership and intent
   * @default - None
   */
  context: string
  
  /**
   * Stage as identifier
   * @default - None
   */
  stage: TradingStages

  /**
   * K8s Namespace
   * @default - None
   */
   k8sNamespace: K8sNamespace

   /**
    * K8s ServiceAccount for API deployment
    * @default - None
    */
   k8sServiceAccount: K8sServiceAccountApi | K8sServiceAccountCronJob



   /**
    * AWS EKS ClusterId
    * 
    * Only needed if not deploying to Trinity or Blade, e.g. to a short lived test cluster - 
    * please use the Cluster ID which is part of API Server endpoint
    * 
    */
   eksClusterId?: string
}
export class AwsIrsaAppAssetsStack extends Stack {

  private readonly stage: TradingStages;
  private readonly context: string;

  private namePrefix() {
    return `${this.stage}-${this.context}`;
  }

  constructor(scope: Construct, id: string, props: AwsIrsaAppAssetsStackProperties) {
    super(scope, id, props);

    this.stage = props.stage;
    this.context = props.context;
    
    //AWS IAM Role for ServiceAccount
    const irsaAppRole = new IrsaRole(this,"irsa-app-role",{
      context: props.context,
      stage: props.stage,
      k8sNamespace: props.k8sNamespace,
      k8sServiceAccountName: props.k8sServiceAccount,
      eksClusterId: props.eksClusterId
    })

    const globalTelemetryPolicy = ManagedPolicy.fromManagedPolicyName(this,"globalTelemetryPolicy",`${this.namePrefix()}-irsa-common-app-telemetry`);
    irsaAppRole.iamRoleInstance.addManagedPolicy(globalTelemetryPolicy);

  }
}