ALL_TASKS_INFO = {
    "operationName": "CampaignActivitiesPanel",
    "variables": {
        "campaignId": "f7e24f14-b911-4f11-b903-edac89a095ec",
        "isTrusted": True,
    },
    "query": "fragment ActivityFields on CampaignActivity {\n  id\n  createdAt\n  updatedAt\n  startDateTimeAt\n  endDateTimeAt\n  title\n  description\n  coverAssetUrl\n  type\n  identityType\n  recurringPeriod {\n    count\n    type\n    __typename\n  }\n  recurringMaxCount\n  properties\n  records {\n    id\n    status\n    createdAt\n    activityId\n    properties\n    rewardRecords {\n      id\n      status\n      appliedRewardType\n      appliedRewardQuantity\n      appliedRewardMetadata\n      error\n      rewardId\n      reward {\n        id\n        quantity\n        type\n        properties\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  tags {\n    id\n    name\n    __typename\n  }\n  reward {\n    id\n    title\n    description\n    quantity\n    type\n    imageUrl\n    properties\n    __typename\n  }\n  targetReward {\n    id\n    activityId\n    missionId\n    __typename\n  }\n  nft {\n    id\n    tokenId\n    name\n    description\n    image\n    properties\n    mintPrice\n    platformFee\n    maxSupply\n    maxMintCountPerAddress\n    nftContract {\n      id\n      address\n      type\n      chainId\n      __typename\n    }\n    __typename\n  }\n  isHidden\n  __typename\n}\n\nfragment MissionFields on CampaignMission {\n  id\n  createdAt\n  updatedAt\n  startDateTimeAt\n  endDateTimeAt\n  title\n  description\n  coverPhotoUrl\n  recurringPeriod {\n    count\n    type\n    __typename\n  }\n  recurringMaxCount\n  properties\n  tags {\n    id\n    name\n    __typename\n  }\n  rewards {\n    id\n    title\n    description\n    quantity\n    type\n    imageUrl\n    properties\n    awardMechanism\n    __typename\n  }\n  records {\n    id\n    status\n    createdAt\n    missionId\n    rewardRecords {\n      id\n      status\n      appliedRewardType\n      appliedRewardQuantity\n      appliedRewardMetadata\n      error\n      rewardId\n      reward {\n        id\n        quantity\n        type\n        properties\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  activities {\n    id\n    __typename\n  }\n  isHidden\n  __typename\n}\n\nfragment CampaignCommunityGoalFields on CampaignCommunityGoal {\n  id\n  title\n  description\n  additionalDetails\n  imageUrl\n  threshold\n  status\n  startDateTimeAt\n  endDateTimeAt\n  createdAt\n  updatedAt\n  isThresholdHidden\n  isHidden\n  ctaButtonCopy\n  ctaButtonUrl\n  __typename\n}\n\nquery CampaignActivitiesPanel($campaignId: String!) {\n  campaign(id: $campaignId) {\n    activities {\n      ...ActivityFields\n      __typename\n    }\n    missions {\n      ...MissionFields\n      __typename\n    }\n    communityGoals {\n      ...CampaignCommunityGoalFields\n      activity {\n        ...ActivityFields\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}

FOLLOW_MICHAEL_HEINRICH_CEO_0G_LABS = {
    "operationName": "VerifyActivity",
    "variables": {"data": {"activityId": "1cd50bdf-fe19-424d-8d92-744f0ff9ace1"}},
    "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}

FOLLOW_MING_WU_CEO_0G_LABS = {
    "operationName": "VerifyActivity",
    "variables": {"data": {"activityId": "fd912f44-772e-4919-826e-b2bd5fa93e02"}},
    "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}


FOLLOW_0G_FOUNDATION = {
    "operationName": "VerifyActivity",
    "variables": {"data": {"activityId": "67b20482-57e2-4ed4-a5fc-88ff66a8559d"}},
    "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}

FOLLOW_0G_LABS = {
    "operationName": "VerifyActivity",
    "variables": {"data": {"activityId": "6bbd5c7e-ad18-4274-8a9c-ed26a4f047f3"}},
    "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}

FOLLOW_ONE_GRAVITY_THE_FIRST_NFT_COLLECTION_ON_0G = {
    "operationName": "VerifyActivity",
    "variables": {"data": {"activityId": "9673d2ce-c6c8-441e-b420-09ea82a39a6e"}},
    "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}

FOLLOW_AI_VERSE_COMING_SOON = {
    "operationName": "VerifyActivity",
    "variables": {"data": {"activityId": "9be09897-1eba-4cd4-98c0-f39c0a56600f"}},
    "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}

FOLLOW_BATTLE_OF_AGENTS_COMING_SOON = {
    "operationName": "VerifyActivity",
    "variables": {"data": {"activityId": "95ea2d98-147b-4683-b5c7-a76d3f43af47"}},
    "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}

DAILY_CHECK_IN = {
    "operationName": "VerifyActivity",
    "variables": {"data": {"activityId": "c35c81a8-b46b-427a-b1f6-f30a1a65691d"}},
    "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
}

USER_INFO = {
    "operationName": "UserMe",
    "variables": {"campaignId": "f7e24f14-b911-4f11-b903-edac89a095ec"},
    "query": "fragment RecordFields on CampaignSpot {\n  records {\n    id\n    status\n    properties\n    points\n    instanceCount\n    createdAt\n    updatedAt\n    activityId\n    activity {\n      id\n      title\n      description\n      type\n      __typename\n    }\n    mission {\n      id\n      title\n      description\n      __typename\n    }\n    communityGoal {\n      id\n      title\n      description\n      threshold\n      __typename\n    }\n    rewardRecords {\n      id\n      status\n      appliedRewardType\n      appliedRewardQuantity\n      appliedRewardMetadata\n      error\n      rewardId\n      reward {\n        id\n        quantity\n        type\n        properties\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery UserMe($campaignId: String!) {\n  userMe {\n    id\n    campaignSpot(campaignId: $campaignId) {\n      id\n      points\n      referralCode\n      referralCodeEditsRemaining\n      ...RecordFields\n      __typename\n    }\n    __typename\n  }\n}",
}


def get_verify_activity_json(referral_code: str = None) -> dict:
    return {
        "operationName": "VerifyActivity",
        "variables": {
            "data": {
                "activityId": "8cdc0521-90c1-435e-b108-78761eb9e60a",
                "metadata": {"referralCode": referral_code},
            }
        },
        "query": "mutation VerifyActivity($data: VerifyActivityInput!) {\n  verifyActivity(data: $data) {\n    record {\n      id\n      activityId\n      status\n      properties\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    missionRecord {\n      id\n      missionId\n      status\n      createdAt\n      rewardRecords {\n        id\n        status\n        appliedRewardType\n        appliedRewardQuantity\n        appliedRewardMetadata\n        error\n        rewardId\n        reward {\n          id\n          quantity\n          type\n          properties\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
    }
