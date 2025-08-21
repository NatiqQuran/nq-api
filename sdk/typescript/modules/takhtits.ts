import * as TakhtitsType from "../types/takhtits";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class TakhtitsController extends BaseController {

    constructor(connection: Connection, token?: string) {
        super(connection, token);
    }
    
    /** GET /takhtits/ */
    async list(config?: RequestConfig<TakhtitsType.TakhtitsListRequestParams>
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsListResponseData>> {
        return await this.axiosGet(`/takhtits/`, config);
    }
    
    /** POST /takhtits/ */
    async create(data: TakhtitsType.TakhtitsCreateRequestData,config?: RequestConfig
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsCreateResponseData>> {
        return await this.axiosPost(`/takhtits/`, data, config);
    }
    
    /** GET /takhtits/{uuid}/ */
    async retrieve(uuid: string,config?: RequestConfig
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsRetrieveResponseData>> {
        return await this.axiosGet(`/takhtits/${uuid}/`, config);
    }
    
    /** PUT /takhtits/{uuid}/ */
    async update(uuid: string,data: TakhtitsType.TakhtitsUpdateRequestData,config?: RequestConfig
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsUpdateResponseData>> {
        return await this.axiosPut(`/takhtits/${uuid}/`, data, config);
    }
    
    /** PATCH /takhtits/{uuid}/ */
    async partialUpdate(uuid: string,data: TakhtitsType.TakhtitsPartialupdateRequestData,config?: RequestConfig
    ): Promise<AxiosResponse<TakhtitsType.TakhtitsPartialupdateResponseData>> {
        return await this.axiosPatch(`/takhtits/${uuid}/`, data, config);
    }
    
    /** DELETE /takhtits/{uuid}/ */
    async delete(uuid: string,config?: RequestConfig
    ): Promise<AxiosResponse<any>> {
        return await this.axiosDelete(`/takhtits/${uuid}/`, config);
    }
    
}