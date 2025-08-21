import * as HealthType from "../types/health";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class HealthController extends BaseController {

    constructor(connection: Connection, token?: string) {
        super(connection, token);
    }
    
    /** GET /health/ */
    async list(config?: RequestConfig
    ): Promise<AxiosResponse<HealthType.HealthListResponseData>> {
        return await this.axiosGet(`/health/`, config);
    }
    
}